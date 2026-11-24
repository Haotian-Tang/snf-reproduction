#!/usr/bin/env Rscript
# Run from the project root, normally through the Quarto report / Pixi task.
options(stringsAsFactors = FALSE)
stopifnot(requireNamespace("survival", quietly = TRUE),
          requireNamespace("jsonlite", quietly = TRUE))
config <- jsonlite::fromJSON("config/analysis.json")
stopifnot(config$distance == "Euclidean", config$normalization == "as supplied",
          config$K > 0, config$K < config$expected_patients,
          config$alpha > 0, config$iterations > 0, config$clusters > 1)
stopifnot(system2("python", c("scripts/fetch_data.py", "--verify-only")) == 0L)
dir.create(config$results_dir, showWarnings = FALSE, recursive = TRUE)
out <- function(name) file.path(config$results_dir, name)
source_dir <- file.path(config$raw_dir, "SNFtool", "R")
stopifnot(dir.exists(source_dir))
for (f in sort(list.files(source_dir, pattern = "\\.[Rr]$", full.names = TRUE))) source(f)
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
seed <- as.integer(config$seed)
dput(config, out("config.R"))
file.copy("config/analysis.json", out("config.json"), overwrite = TRUE)

# The original files have doubled header tabs / trailing tabs. Whitespace parsing
# avoids creating fictitious columns full of NA. Do not change downloaded files.
read_omics <- function(path) {
  ids <- scan(path, what = "", nlines = 1, quiet = TRUE)
  x <- read.table(path, skip = 1, header = FALSE, row.names = 1,
                  col.names = c("feature", ids), check.names = FALSE)
  stopifnot(ncol(x) == length(ids), !anyNA(x), !anyDuplicated(rownames(x)))
  x <- t(as.matrix(x))
  patient <- substr(rownames(x), 1, 12)
  stopifnot(!anyDuplicated(patient), all(is.finite(x)))
  rownames(x) <- patient
  x
}
prefix <- file.path(config$raw_dir, "Breast", "BREAST_")
views <- list(mRNA = read_omics(paste0(prefix, "Gene_Expression.txt")),
              Methylation = read_omics(paste0(prefix, "Methy_Expression.txt")),
              miRNA = read_omics(paste0(prefix, "Mirna_Expression.txt")))
clinical <- read.table(paste0(prefix, "Survival.txt"), header = TRUE)
clinical$patient <- substr(clinical$PatientID, 1, 12)
stopifnot(!anyDuplicated(clinical$patient))
ids <- clinical$patient
stopifnot(length(ids) == config$expected_patients,
          all(vapply(views, function(x) setequal(rownames(x), ids), logical(1))),
          !anyNA(clinical), sum(clinical$Death) == config$expected_deaths,
          all(clinical$Death %in% c(0, 1)), all(clinical$Survival >= 0))
views <- lapply(views, function(x) x[ids, , drop = FALSE])
qc <- do.call(rbind, lapply(names(views), function(nm) {
  x <- views[[nm]]
  data.frame(view = nm, patients = nrow(x), features = ncol(x), missing = sum(is.na(x)),
             max_abs_feature_mean = max(abs(colMeans(x))),
             min_feature_sd = min(apply(x, 2, sd)), max_feature_sd = max(apply(x, 2, sd)))
}))
write.table(qc, out("data_qc.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
stopifnot(all(qc$max_abs_feature_mean < 1e-5),
          all(qc$features == unlist(config$expected_features[qc$view])))
# Inputs already have population-SD normalization. Do not log-transform / z-score again.
distances <- lapply(views, function(x) sqrt(dist2(x, x)))
graphs <- lapply(distances, affinityMatrix, K = config$K, sigma = config$alpha)
fused <- SNF(graphs, K = config$K, t = config$iterations)
stopifnot(all(is.finite(fused)), min(fused) >= 0,
          max(abs(fused - t(fused))) < config$validation$matrix_tolerance)
all_graphs <- c(graphs, list(SNF = fused))
cluster_one <- function(w) {
  set.seed(seed)
  as.integer(SpectralClustering(w, config$clusters))
}
labels <- lapply(all_graphs, cluster_one)
logrank <- function(g) {
  fit <- survival::survdiff(survival::Surv(Survival, Death) ~ factor(g), data = clinical)
  pchisq(fit$chisq, length(fit$n) - 1L, lower.tail = FALSE)
}
paper_p <- unlist(config$paper$logrank_p)
metrics <- do.call(rbind, lapply(names(labels), function(nm) {
  g <- labels[[nm]]
  data.frame(method = nm, logrank_p = logrank(g), paper_p = paper_p[[nm]],
             cluster_sizes = paste(tabulate(g, config$clusters), collapse = "/"),
             deaths = sum(clinical$Death), patients = nrow(clinical))
}))
write.table(metrics, out("survival_comparison.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
assignments <- cbind(clinical, as.data.frame(labels))
write.table(assignments, out("patient_clusters.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
dimnames(fused) <- list(ids, ids)
write.table(fused, out("fused_network.tsv"), sep = "\t", quote = FALSE, col.names = NA)

palette <- grDevices::hcl.colors(config$clusters, palette = "Dark 3")
draw_km <- function(g, title) {
  fit <- survival::survfit(survival::Surv(Survival / config$days_per_month, Death) ~ factor(g), data = clinical)
  plot(fit, col = palette, lwd = 2, conf.int = FALSE, mark.time = TRUE,
       xlab = "Follow-up (months)", ylab = "Overall survival probability",
       main = title, ylim = c(0, 1), bty = "l", las = 1)
  legend("bottomleft", legend = paste0("Cluster ", seq_len(config$clusters), " (n=", tabulate(g, config$clusters), ")"),
         col = palette, lwd = 2, cex = 0.75, bty = "n")
  mtext(sprintf("Log-rank p = %.3g; %d deaths / %d patients", logrank(g),
                sum(clinical$Death), nrow(clinical)), side = 3, line = 0.25, cex = 0.8)
}
png(out("figure1_networks.png"), width = 2200, height = 850, res = 160)
par(mfrow = c(1, 4), mar = c(3, 1, 3, 1), oma = c(3, 2, 2, 1), cex = 1)
ord <- order(labels$SNF, ids)
for (nm in names(all_graphs)) {
  w <- all_graphs[[nm]]
  diag(w) <- 0
  w <- w[ord, ord]
  # Per-panel scaling is explicit: shows topology, not comparable weight magnitudes.
  cap <- as.numeric(quantile(w[row(w) != col(w)], 0.99))
  w <- pmin(w / cap, 1)
  image(seq_along(ids), seq_along(ids), t(w[nrow(w):1, ]),
        col = colorRampPalette(c("#FFFFFF", "#C6DBEF", "#2171B5", "#08306B"))(100),
        axes = FALSE, xlab = "", ylab = "", main = nm, useRaster = TRUE)
  bounds <- head(cumsum(tabulate(labels$SNF, config$clusters)), -1) + 0.5
  abline(v = bounds, h = length(ids) + 1 - bounds, col = "#999999", lty = 3)
  box()
  mtext("Patients", side = 1, line = 0.6, cex = 0.8)
}
mtext("TCGA breast cancer: individual networks and SNF", outer = TRUE, side = 3, cex = 1.2)
mtext("Same patient order (SNF clusters); each panel scaled to its own off-diagonal 99th percentile",
      outer = TRUE, side = 1, cex = 0.8)
dev.off()

png(out("figure2_embedding_survival.png"), width = 1800, height = 850, res = 160)
par(mfrow = c(1, 2), mar = c(4.5, 4.5, 4, 1), oma = c(2, 0, 1, 0))
pc <- prcomp(fused, center = TRUE, scale. = FALSE)
variance <- 100 * pc$sdev^2 / sum(pc$sdev^2)
plot(pc$x[, 1:2], col = palette[labels$SNF], pch = 19, cex = 0.9,
     xlab = sprintf("PC1 (%.1f%%)", variance[1]), ylab = sprintf("PC2 (%.1f%%)", variance[2]),
     main = "A  PCA of the fused network", bty = "l", las = 1)
legend("topright", paste("Cluster", seq_len(config$clusters)), col = palette, pch = 19, bty = "n", cex = 0.75)
draw_km(labels$SNF, "B  SNF clusters: overall survival")
mtext("Analogous to Supplementary Figure 15 (BIC); 2D projection and independent analysis, not an exact reconstruction",
      side = 1, outer = TRUE, cex = 0.75)
dev.off()

png(out("figure3_survival_comparison.png"), width = 1700, height = 1400, res = 160)
par(mfrow = c(2, 2), mar = c(4.5, 4.5, 4, 1))
for (nm in names(labels)) draw_km(labels[[nm]], nm)
dev.off()

# Recompute the primary analysis (same inputs/config/seed), compare numerical
# networks and partition equivalence; never compare cluster IDs literally.
repeated <- SNF(graphs, K = config$K, t = config$iterations)
again <- cluster_one(repeated)
checks <- c(network_max_abs_difference = max(abs(fused - repeated)),
            partition_pairwise_identical = identical(outer(labels$SNF, labels$SNF, "=="),
                                                     outer(again, again, "==")))
stopifnot(checks[1] < config$validation$matrix_tolerance, checks[2] == 1)
write.table(data.frame(check = names(checks), value = unname(checks)),
            out("repeatability.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

# A predeclared diagnostic, not a search for the paper's p-value. The bundled
# 2013 README calls dist2 directly (squared distance), whereas the paper says
# Euclidean. Show both conventions and t=10/20 without selecting by survival.
ari <- function(a, b) {
  choose2 <- function(x) x * (x - 1) / 2
  tab <- table(a, b); n <- sum(tab)
  index <- sum(choose2(tab)); ra <- sum(choose2(rowSums(tab))); cb <- sum(choose2(colSums(tab)))
  expected <- ra * cb / choose2(n)
  (index - expected) / ((ra + cb) / 2 - expected)
}
grid <- expand.grid(distance = config$diagnostics$distance,
                    iterations = config$diagnostics$iterations,
                    K = config$diagnostics$K, stringsAsFactors = FALSE)
diagnostics <- do.call(rbind, lapply(seq_len(nrow(grid)), function(i) {
  row <- grid[i, ]
  ds <- if (row$distance == "Euclidean") distances else lapply(distances, function(d) d^2)
  gs <- lapply(ds, affinityMatrix, K = row$K, sigma = config$alpha)
  w <- SNF(gs, K = row$K, t = row$iterations)
  g <- cluster_one(w)
  cbind(row, logrank_p = logrank(g), ARI_to_primary = ari(labels$SNF, g),
        cluster_sizes = paste(tabulate(g, config$clusters), collapse = "/"))
}))
write.table(diagnostics, out("diagnostics.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
saveRDS(list(config = config, graphs = all_graphs, labels = labels, clinical = clinical,
             qc = qc, metrics = metrics, diagnostics = diagnostics, repeatability = checks),
        out("analysis.rds"), version = 3)
capture.output(sessionInfo(), file = out("sessionInfo.txt"))
print(qc)
print(metrics)
print(checks)
print(diagnostics)

# Reproducing SNF on the original TCGA breast cancer cohort

本项目使用 Wang et al. (2014) 随论文发布的处理后 TCGA 乳腺癌数据及原始 R 软件，尝试重现患者网络、5 类分群与生存分析。它是 CBIO7501 开放科学案例的实践证据，**尚未精确重现原文数值，不是可直接提交的两页作业报告**。

## Run

在本目录执行（需要 R、R 的推荐包 `survival`；下载另需 curl/unzip）：

```sh
sh scripts/download.sh
Rscript --vanilla scripts/reproduce.R
```

数据和原版 R 源码已下载，所以当前电脑可以直接运行第二条命令。不需要安装现代 SNFtool；脚本直接加载 `vendor/SNFtool/R/` 的原版函数，未修改作者代码。

已验证环境：R 4.6.1；`survival` 的确切版本及系统信息见 `results/sessionInfo.txt`。数据/源码由 SHA-256 固定，参数及 RNG 明确记录；**没有声称建立容器或实现跨平台位级一致性**。使用其他 R/BLAS 版本时需要重新检查分群。`survival` 随标准 R 推荐包提供，精确版本以已验证环境记录为准。

## Inputs and provenance

原文：Wang B, Mezlini AM, Demir F, et al. *Similarity network fusion for aggregating data types on a genomic scale*. Nature Methods 11, 333–337 (2014). DOI: https://doi.org/10.1038/nmeth.2810

- 出版社页面：https://www.nature.com/articles/nmeth.2810
- `MOESM206`：作者预处理后的 TCGA 癌症数据；仅提取 Breast 文件夹。
- `MOESM205`：原始 SNFtool 1.2，2013 年的软件附件，DESCRIPTION 标为 GPL；vendor 内保留原始归属信息。不要将其许可自动套用于数据。
- `MOESM204`：补充方法、表和图。主要参照 Supplementary Figure 15 的 BIC 栏，以及主文 Table 1。
- 完整下载 URL 见 `scripts/download.sh`；SHA-256 见 `checksums-downloads.sha256` 和 `checksums-inputs.sha256`。首次下载日期：2026-10-23。

研究范围是从作者提供的处理后矩阵开始的**下游计算复现尝试**；不包括原始 TCGA level-3 数据的过滤、KNN 插补和归一化的独立复现。原文乳腺癌 mRNA 来自 Agilent 微阵列、甲基化来自 HM27，不能与此前讨论的现代 BRCA RNA-seq/HM450 队列混为一谈。

## Primary analysis (chosen before viewing survival results)

- 105 位患者，三个组学和临床表的患者集合完全匹配。
- 17,814 mRNA 特征；23,094 甲基化探针；**354 miRNA 特征**。
- 依据 TCGA 条码前 12 位匹配患者，检查无重复；按临床表顺序重新排列。
- 原附件已归一化、无缺失值，不额外筛特征、插补或 log 转换。
- 欧氏距离；K=20；alpha=0.5；20 次融合；5 类；随机种子 20261023。
- 用原附件的 `SpectralClustering`；单组学和融合网络采用同一聚类实现及类别数。
- 用 `survival::survdiff` 的渐近卡方 log-rank 检验；画总体生存 Kaplan–Meier 曲线。
- `Survival` 按天处理，图中除以 30.4375 转为月；事件按附件 `Death` 0/1 使用。

K/alpha/t 是公开示例及方法范围内的明确设置，**尚未找到逐队列的完整原始运行脚本来确认它们就是论文 BIC 实验的确切设置**。5 类沿用论文的 BIC 结果，不在本项目重新验证最优类别数。

## First results

| Method | Our log-rank p | Paper Table 1 p |
|---|---:|---:|
| mRNA | 0.005876 | 0.03 |
| Methylation | 0.242002 | 0.05 |
| miRNA | 0.009465 | 0.30 |
| SNF | 0.007006 | 0.0011 |

SNF 分群人数为 23/24/19/19/20；共有 18 个死亡事件。当前结果**不能证明 SNF 比所有单组学更优**，也没有准确重现原文 p 值。尾部生存曲线可能由很少的在险患者决定；分群不是经过临床验证的新亚型。

同一输入、参数和随机种子再次计算，融合矩阵最大绝对差为 0，患者分群的成对共组关系完全一致。这说明当前环境下可重复计算，并不证明复现了作者的全部分析。

## Figures

1. `results/figure1_networks.png`：三个单组学和融合网络的对照热图。同一患者顺序按 SNF 分群排列；对角线置零仅用于绘图，每幅按自身非对角线第 99 百分位缩放。色深不能用来跨组学比较绝对相似性。融合图的块状结构部分来自按其自身分群排序，不是独立验证。
2. `results/figure2_embedding_survival.png`：融合网络的二维 PCA 和 SNF 分群生存曲线，形式对应补充图 15 的 BIC 栏。原图为三维且没有提供可直接核对的坐标/标签；这里明确用中心化融合矩阵的前两主成分，属于相似图，不能称像素级重建。
3. `results/figure3_survival_comparison.png`：单组学和 SNF 的生存曲线对照。

## Reproducibility findings

1. **原表格格式陷阱**：mRNA 表头有双制表符，数值行有尾部制表符。直接 `read.delim` 会产生虚假的空列/缺失值。本脚本将表头和数值分开按空白读取，并验证列数及患者 ID，不修改原文件。
2. **附件与补充表特征数不符**：补充表 1 的 BIC miRNA 为 1,046，实际可下载 Breast miRNA 文件为 354 行。目前无法确认是附件版本、未说明过滤还是文档问题，不自行补齐或编造解释。
3. **距离定义不一致**：论文方法写欧氏距离，但 2013 软件 README 直接调用返回平方欧氏距离的 `dist2`。主分析使用欧氏距离；另存两种距离、t=10/20、K=15/20/25 的完整诊断表，不依 p 值选择设置。
4. **代码版本重要**：这是原始补充 R 软件，不是现代 CRAN SNFtool。论文称主要实验用 MATLAB 实现，R 版本由另一作者提供；跨实现的精确对应仍需检查，不能把差异只归因于某一个问题。
5. **参数稳定性不等于重复运行**：当前欧氏距离下，K 从 20 改为 15/25，分群相对主分析的 ARI 约为 0.495/0.641。相同设置重复运行完全一致，但合理改变设置会改变分群。

数据开放和配套代码使独立再分析成为可能；未明确冻结的运行设置、输入版本和实现差异仍可能妨碍数值级复现。这比“图看起来相似，所以复现成功”更适合作业的批判性讨论。

## Outputs

`data_qc.tsv` 数据检查；`patient_clusters.tsv` 临床及分群；`fused_network.tsv` 融合矩阵；`survival_comparison.tsv` 原文对照；`diagnostics.tsv` 完整诊断；`repeatability.tsv` 重跑检查；`config.R` 参数；`sessionInfo.txt` 环境；`analysis.rds` 中间对象。

## AI disclosure draft

“I used OpenAI Codex to assist with locating public resources, writing and running analysis code, and documenting reproducibility checks. I reviewed the methods, outputs, and interpretation.”

提交前应按自己实际完成的审阅工作修改，不能声称完成了尚未进行的人工验证。

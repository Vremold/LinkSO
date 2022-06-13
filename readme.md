# Link Stack Overflow to Programming language textbooks

## Introduction

本文的出发点利用Stack Overflow问答帖中蕴含的语用知识弥补编程语言教材中这方的不足。那么我们做这个工作的思路就很明了了
1. 首先训练一个二分类器将那些不包含编程语言语用（开发）知识的问答帖过滤掉，本文标注了一部分数据，总共有8000条，正面和负面数据各占一半，使用基于[roberta](https://huggingface.co/roberta-base)预训练模型进行预测，准确率比较好
2. 其实我们就要把SO和教材的章节连接起来，进一步，我们只需要计算出来一个SO帖子和教材章节的匹配分数即可，本工作采取的方案是递进的，即先匹配章，后匹配节。那么怎么计算一个SO问答帖和一个章（节）的匹配分数呢？本文选用的思路是**从关键词**，从**隐式语义**，**从代码元素**给出匹配分数，总的匹配分数就是它们的加权平均。
    1. 从关键词：本工作选用了两个方案，一个是[mprank](https://arxiv.org/abs/1803.08721)，另一个直接字符串抽取，当然是mprank更好了。
    2. 从隐式语义：本工作同样实现了两个方案，一个基于word2vec，另外一个基于[sentence-bert](https://www.sbert.net/)，当然也是sentence-bert更好。
    > 有研究指出sentence-bert后面应该再加个[白化](https://kexue.fm/archives/8069)，就是得到嵌入向量（768维）后再进行一个PCA主成分抽取，但是因为时间缘故，目前没做(笑)
    3. 从代码元素：严格来说，本文也实现了两个方案，一种是使用javalang抽取代码片段中的API，但因为目前的研究范围限定为JDK，其实这个意义不大，因此本工作才用了另外一个方案就是直接从代码片段中匹配JDK中的代码元素（包、类、接口、异常、方法等）

## How to Run

- 环境要求：Python 3.7
- ```pip install requirements.txt```
- 运行细节
  - JDKCrawler里面存放的是JDK中所有API的爬取项目，运行crawler_v2.py文件即可
  - 标有DataClean的文件夹里面存放的数据预处理过程，包括SO数据的预处理，以及三本教材（*Think In Java*, *Core Java Volume 1*, *Core Java Volume 2*）的预处理。（其实还有*Effective Java*，不过后来发现这本教材的数据难以利用），里面的所有py文件都已经按照序号标注了，只要按照顺序运行即可。
  - SOPostClassifier文件夹里面存放的是SO帖子分类器的训练，最佳模型时roberta-base+dense，里面还有一些机器学习的模型，当然还有一个roberta-base+dense的多卡版本，但是没有训练，不保证对
  - 项目中标有Validation的文件夹里面存放的全是不同方面验证的文件，进入每个验证文件夹下根据名称大概就能判断如何运行的了，注意不同教材的运行可能需要改动match_config中的教材名字。
  - PS：请一定注意config.py文件中的路径名和其他配置，如果出现问题，建议先看这里。有些过深的文件夹中用的可能是绝对路径，如果自己想运行，建议修改。

## Dataset

大部分处理数据都在项目中了。
RawData以及SO数据太大，后续将会上传网盘，并将连接放在这里……又挖了一个坑(笑)
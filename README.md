# My experiments with delta format

The goal was to:
1. Investigate how to use delta format in python
2. Check the schema evolution and protection mechanisms in delta

## Install

Prerequisites:
1. spark = 3.2.1
2. python = ^3.10

Run script:
1. git clone ssh://git@github.com:zhukovgreen/delta-lake-experiments.git
2. poetry install
3. poetry run pytest test_playground.py 

# Delta format

![](https://i.imgur.com/xVw8E3F.png)

---

This presentation is about my findings when
I was playing with the delta format (https://delta.io/)
during my trip in a train from the NEO event.

It is not a comprehensive overview, but it signifies 
things which I liked especially.

---

## Intro

Apache Spark is first class citizen in the world of the big data (to be honest, I don't know anything else which is proven to be as a second option).

Delta Lake is the file format to store and query efficiently the big ammount of data

All these are open sourced projects

---

## Still parquet as underlying data format

- strongly typed
- immutable
- compressed

---

## Interesting properties

---

Partitions can be replaced without rewriting all the data
![](https://i.imgur.com/eI789xx.png)

---

Each job is atomic (success or no changes to the original state)
```bash
# rename operation (starts)
/table
  /INFORMATION_DATE=2021-10-19
    A-00001.parquet
    A-00002.parquet
 /_tmp
    /INFORMATION_DATE=2021-10-20
       B-00001.parquet
       B-00002.parquet.part
```
```bash
# rename operation (done)
/table
  /INFORMATION_DATE=2021-10-19
    A-00001.parquet
    A-00002.parquet
  /INFORMATION_DATE=2021-10-20
     B-00001.parquet
     B-00002.parquet.part
```

same applies to the spark structured streaming (minibatches)

---

transaction log. You can see it as the git repository's .git directory.

(show in hands on project)

---

Time traveling (possible due to the previous feature)

![](https://i.imgur.com/HcKa25X.png)

---

Schema evolution

- Schema validation on write (shown in hands on)
- Schema evolution for adding columns
- Changes data types of columns (needs rewrite + overwriteSchema=true)
- Adding the partial dataframe (subset of columns)

---
![](https://i.imgur.com/CVSBWmU.png)

---

Replacing single partition

![](https://i.imgur.com/TqGRr2Z.png)


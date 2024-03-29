# -*- coding: utf-8 -*-
"""(13) Fine_Tuning_Sentiment_Analysis_Multiple_Inputs_RTE.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1areHUpEK32tApQDNEyqCqF8iLGddq3Gn

# <b>Importing libraries:</b>
"""

!pip install transformers[torch]
!pip install accelerate -U

!pip install transformers datasets

import numpy as np
import pandas as pd
# import seaborn as sn
# import matplotlib.pyplot as plt
import torch
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix
# from sklearn.model_selection import train_test_split
from datasets import load_dataset

"""# <b> Dataset:</b>"""

# The Recognizing Textual Entailment (RTE) datasets come from a series of annual
# textual entailment challenges. We combine the data from RTE1 (Dagan et al.,
# 2006), RTE2 (Bar Haim et al., 2006), RTE3 (Giampiccolo et al., 2007), and RTE5
# (Bentivogli et al., 2009).4 Examples are constructed based on news and
# Wikipedia text. We convert all datasets to a two-class split, where for
# three-class datasets we collapse neutral and contradiction into not
# entailment, for consistency.

raw_data = load_dataset("glue", "rte")

"""# <b>Explore the Data:</b>"""

raw_data

raw_data['train'][0]

raw_data['train'].features

"""# <b>Tokenizer:</b>"""

from transformers import AutoTokenizer

checkpoint = 'distilbert-base-cased'

tokenizer = AutoTokenizer.from_pretrained(checkpoint)

def tokenizer_func(batch):
  return tokenizer(batch['sentence1'], batch['sentence2'], truncation=True)

tokenized_data = raw_data.map(tokenizer_func, batched=True)

tokenizer(
    raw_data['train']['sentence1'][0],
    raw_data['train']['sentence2'][0],
)

result = _ #The same as tokenized_data

tokenized_data.keys()

result.keys()

tokenizer.decode(result['input_ids'])

"""# <b>Load the model and model arguments:</b>"""

!ls

from transformers import TrainingArguments, Trainer, AutoModelForSequenceClassification

training_args = TrainingArguments(
    output_dir='my_trainer',
    evaluation_strategy='epoch',
    save_strategy='epoch',
    num_train_epochs=5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    logging_steps=150
)

model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

"""#<b>Model Summary:</b>"""

type(model)

model

!pip install torchinfo

from torchinfo import summary
summary(model)

"""#<b>Training:</b>

1. Metrics:
"""

from datasets import load_metric

metric = load_metric('glue', 'rte')

metric.compute(predictions=[1, 0, 1], references=[1, 0, 0])

def compute_metrics(logits_and_labels):
  logits, labels = logits_and_labels
  predictions = np.argmax(logits, axis=-1)
  acc_ = np.mean(predictions == labels)
  f1_ = f1_score(labels, predictions) #, average='macro'
  return {'accuracy': acc_, 'f1': f1_}
  # print('accuracy': acc_ , 'f1': f1_)

"""2. Trainer:"""

from transformers import Trainer

trainer = Trainer(
    model,
    training_args,
    train_dataset = tokenized_data['train'],
    eval_dataset = tokenized_data['validation'],
    tokenizer = tokenizer,
    compute_metrics = compute_metrics
)

trainer.train()

"""# <b>Save Model and Pipeline:</b>"""

trainer.save_model('my_saved_rte_model')

from transformers import pipeline

p = pipeline("text-classification", model='my_saved_rte_model')

p({'text': 'I went to the store', 'text_pair': 'I am a bird'})


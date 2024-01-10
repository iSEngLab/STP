import time

import common
from commonApi import read_conf
from gen import gen
from transformers import pipeline

model_checkpoint = "Helsinki-NLP/opus-mt-en-zh"
translator = pipeline(task="translation", model=model_checkpoint)
read_conf()

# dataset = sys.argv[1]
dataset = "Opinion"
orig_sent = []
gen_sent = []
gen_sen_translate = []

# read original sentences
with open("./data/{}".format(dataset), "r", encoding="utf8") as f:
    for line in f.readlines():
        if len(line.strip()) > 0:
            orig_sent.append(line.strip())

# step1 gen
start = time.time()
for origs in orig_sent:
    print(origs)
    gen_sent.append(gen(origs))

print("consume1 %.2f seconds" % (time.time() - start))
start = time.time()

# translate
for gens in gen_sent:
    gen_sen_translate.append([translator(gen)[0]["translation_text"] for gen in gens])  # type: ignore

print("consume2 %.2f seconds" % (time.time() - start))
print("gen %d sentences in all" % sum([len(x) for x in gen_sent]))


common.nlpEN.close()

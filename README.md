# GeoGuessr

The aim of GeoGuessr is to determine the location of a picture, based only of its visual content.
You can try and play with it online [here](https://ai-geoguessr.streamlit.app/).

## Local Installation

You can install GeoGuessr as a regular Python library. It has been designed to work with Python 3.8+. It's best to use a virtual env.

To create your env (only once), you can use :

```bash
virtualenv -p python3.8 env
ln -s env/bin/activate
source activate

pip install -r requirements.txt
```
## Try this feature locally

To test this geolocation feature, or play a 10-points GeoGuessr game against the AI, just run:

```bash
streamlit run app.py --server.port 8008
```

You can also watch a 3-minutes [video demo](https://www.dailymotion.com/video/k73gnVtmRWypVMyvyTp?playlist=x7ncy4).

## Explanations

### Ontology

An [ontology](https://docs.google.com/spreadsheets/d/1n6fD4kvYS4ol1Z3M_CDKlzTVX6mqYytCJWsL-NdYC1I/edit?usp=sharing) of places have been constructed thanks to a list of the [most populated cities in the world](https://data.mongabay.com/cities_pop_03.htm).

As of today, we support ~ 3000 cities and ~ 60 famous monuments or places.

This ontology has up to 4 levels:
`Country > State > City > Monument/Place`
For example:
- `France > Paris > Eiffel Tower`
- `United States > California > Los Angeles`
- `China > Beijing`

PS: For now, `State` is only available for the United States of America.

### Model

For detection, we use a [CLIP architecture model](https://huggingface.co/laion/CLIP-ViT-B-32-laion2B-s34B-b79K) trained on [2 billions text-image pairs by LAION](https://laion.ai/blog/large-openclip/); thanks to [Open Clip implementation](https://github.com/mlfoundations/open_clip).

It is performed by comparing embedding of a picture with embedding of places around the world; all embeddings computed by the same model mentioned above.

### Rules

To obtain quite good performance, we added some rules to filter results. In the following order, we have:
- A monument/place is detected only if the confidence is above 99%.
- A city is detected if the confidence is above 80%.
- A country is detected either if:
    - The sum of confidences of its cities is above 60%, and at least 2 cities have a confidence above 3%. (Good to deal with countries with few cities in ontology; like Belgium.)
    - The sum of confidences of its cities is above 90%, and at least 5 cities have a confidence above 1%. (Good to deal with countries with numerous cities in ontology; like China.)
- If the country is `United States`, a state is detected if the sum of confidences of its cities is above 50%, and at least 2 cities have a confidence above 3%.

## References

[1] A. Radford, J. Wook Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, Y Mishkin, J. Clark, G. Krueger, I. Sutskever, [*Learning Transferable Visual Models From Natural Language Supervision*](https://arxiv.org/pdf/2103.00020.pdf)
```
@inproceedings{Radford2021LearningTV,
  title={Learning Transferable Visual Models From Natural Language Supervision},
  author={Alec Radford and Jong Wook Kim and Chris Hallacy and A. Ramesh and Gabriel Goh and Sandhini Agarwal and Girish Sastry and Amanda Askell and Pamela Mishkin and Jack Clark and Gretchen Krueger and Ilya Sutskever},
  booktitle={ICML},
  year={2021}
}
```


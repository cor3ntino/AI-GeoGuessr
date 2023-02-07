import torch
import open_clip

from utils import load_df

class Model:

    def __init__(self):

        # Load data
        self.cities, self.places, _, _, _ = load_df("cities-final.tsv")

        # Load model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2B_e16')

        # Load precomputed embeddings
        #self.save_embeddings()
        self.load_embeddings()


    def save_embeddings(self):
        """
        Precompute cities & places embeddings, and store them
        """

        with torch.no_grad():
            cities_tokens = open_clip.tokenize(self.cities)
            cities_features = self.model.encode_text(cities_tokens)
            cities_features /= cities_features.norm(dim=-1, keepdim=True)

            torch.save(cities_features, "precomputed/cities.pt")

            places_tokens = open_clip.tokenize(self.places)
            places_features = self.model.encode_text(places_tokens)
            places_features /= places_features.norm(dim=-1, keepdim=True)

            torch.save(places_features, "precomputed/places.pt")

    def load_embeddings(self):
        """
        Load precomputed cities & places embeddings
        """

        self.cities_features = torch.load("precomputed/cities.pt")
        self.places_features = torch.load("precomputed/places.pt")

    def predict(self, image):

        image = self.preprocess(image).unsqueeze(0)

        with torch.no_grad():#, torch.cuda.amp.autocast():
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            cities_probs = (100.0 * image_features @ self.cities_features.T).softmax(dim=-1)
            places_probs = (100.0 * image_features @ self.places_features.T).softmax(dim=-1)

        return cities_probs, places_probs


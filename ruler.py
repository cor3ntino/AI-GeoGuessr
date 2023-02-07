import torch

from utils import load_df

class Ruler:

    def __init__(self):
        """
        Mode 'rules' or 'best_guess'
        """

        self.cities, self.places, self.places_readable, self.mapping_countries, self.mapping_states = load_df("cities-final.tsv")

        self.place_threshold = 0.99
        self.city_threshold = 0.8

        self.sum_country_threshold1 = 0.6
        self.signifivative_country_threshold1 = 0.03
        self.signifivative_country_min_items1 = 2
        self.sum_country_threshold2 = 0.9
        self.signifivative_country_threshold2 = 0.01
        self.signifivative_country_min_items2 = 5

        self.countries_with_states = ["United States"]
        self.sum_state_threshold = 0.5
        self.signifivative_state_threshold = 0.03
        self.signifivative_state_min_items = 2

    def rule_places(self, places_probs):

        if (val := torch.max(places_probs)) > self.place_threshold:
            return (torch.argmax(places_probs), val)
        else:
            return (-1, 0.)

    def rule_cities(self, cities_probs):

        if (val := torch.max(cities_probs)) > self.city_threshold:
            return (torch.argmax(cities_probs), val)
        else:
            return (-1, 0.)

    def rule_countries(self, cities_probs):

        for country, id_cities in self.mapping_countries.items():
            probs = cities_probs[0][id_cities]

            val = sum(probs)
            if (val > self.sum_country_threshold1 \
                and torch.count_nonzero(probs >= self.signifivative_country_threshold1) >= self.signifivative_country_min_items1) \
                or (val > self.sum_country_threshold2 \
                and torch.count_nonzero(probs >= self.signifivative_country_threshold2) >= self.signifivative_country_min_items2):
                return country, val

        return None, 0.

    def rule_states(self, cities_probs):

        for state, id_cities in self.mapping_states.items():
            probs = cities_probs[0][id_cities]

            if (val := sum(probs)) > self.sum_state_threshold \
                and torch.count_nonzero(probs >= self.signifivative_state_threshold) >= self.signifivative_state_min_items:
                return state, val

        return None, 0.

    def rule_all(self, cities_probs, places_probs):

        ind, val = self.rule_places(places_probs)
        # because of element 'something'
        if ind > 0:
            return ("Place", self.places_readable[ind], val)

        ind, val = self.rule_cities(cities_probs)
        # because of elements 'city' & 'something'
        if ind > 1:
            return ("City", self.cities[ind], val)

        country, val = self.rule_countries(cities_probs)
        if country is not None:

            if country in self.countries_with_states:

                state, val2 = self.rule_states(cities_probs)
                if state is not None:
                    return ("State", state, val2)

            return ("Country", country, val)

        return None

    def get_result(self, cities_probs, places_probs):
        """
        Get readable result
        """

        res = self.rule_all(cities_probs, places_probs)

        if res is None:
            return "##### I am not confident enough to detect a location 😢"

        else:
            type_res, location, val = res
            return f"##### I detect a {type_res} with {round(100 * val.item(), 1)}% confidence\n ##### ➡️ {location}"

    def get_best_country(self, cities_probs, places_probs):

        # Try to find country with places
        ind, val = self.rule_places(places_probs)
        if ind > 0:
            return (self.places_readable[ind].split(", ")[-1], val)

        # Else, return best country guessed
        country_probs = [(country, sum(cities_probs[0][id_cities])) for country, id_cities in self.mapping_countries.items()]
        return max(country_probs, key=lambda item:item[1])

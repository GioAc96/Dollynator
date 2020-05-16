import json
import math
import os
import sys
import random

import jsonpickle

from appdirs import user_config_dir

from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings


class QTable:
    discount = 0.05
    # TODO: set starting values for alpha and beta
    start_alpha = 0
    start_beta = 0

    def __init__(self):
        self.qtable = {}
        self.providers_offers = []
        self.self_state = VPSState()
        self.tree = ""
        self.alphatable = {}
        self.betatable = {}
        pass

    # TODO: important function
    # TODO: update alpha and beta in this function
    def update_qtable(self, other_q_values, amount_mb_tokens_per_usd_per_day):
        """
        Updates the qtable following the QD-learning algorithm.
        QD-learning update for current state (else q-value remains constant):
            Qnew <- Qold - beta * (sum of (Qold - Qrecieved))
                         + alpha * (reward + discount * max(action (qvalue) in next state) - Qold)
        :param other_q_values: The list of q-values received from gossipping with its neighbours
        :param amount_mb_tokens_per_usd_per_day: the reward of the current state at the current time
        """
        return

    # TODO: important function
    # TODO: can choose the old choose_option code (simulated annealing)
    #  , this was a nice solution (is commented out down below)
    #  or can go with something simple like the epsilon-greedy algorithm
    def choose_option(self, providers):
        """
        Pick the option to be chosen for the next replication.
        providers: the providers to pick a choice from.
        :return: provider_name, option_name -> set choise in core config
        """
        return

    # TODO: important function
    def create_child_qtable(self, provider, option, transaction_hash, child_index):
        """
        Creates the QTable configuration for the child agent.
        This is done by copying the own QTable configuration and including the new host provider
        , the parent name and the transaction hash.
        :param provider: the name the child tree name.
        :param transaction_hash: the transaction hash the child is bought with.
        """

        next_state = VPSState(provider=provider, option=option)
        tree = self.tree + "." + str(child_index)
        dictionary = {
            "qtable": self.qtable,
            "alpha": self.alphatable,
            "beta": self.betatable,
            "providers_offers": self.providers_offers,
            "self_state": next_state,
            "transaction_hash": transaction_hash,
            "tree": tree
        }

        filename = os.path.join(user_config_dir(), 'Child_QTable.json')
        with open(filename, 'w') as json_file:
            encoded_dictionary = jsonpickle.encode(dictionary)
            json.dump(encoded_dictionary, json_file)

    # TODO: important function
    def write_dictionary(self):
        """
        Writes the QTABLE configuration to the QTable.json file.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')
        to_save_var = {
            "qtable": self.qtable,
            "alpha": self.alphatable,
            "beta": self.betatable,
            "providers_offers": self.providers_offers,
            "self_state": self.self_state,
            "tree": self.tree
        }
        with open(filename, 'w') as json_file:
            encoded_to_save_var = jsonpickle.encode(to_save_var)
            json.dump(encoded_to_save_var, json_file)

    # TODO: important function
    def read_dictionary(self, providers=None):
        """
        Read the QTable object from file, if there isn't any make one.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')

        if not os.path.exists(filename):
            # There is no QTable.json file, this can only be the case when
            # , the file failed to copy when creating a new child or it runs on local for the first time
            # TODO: Make it a random provider/option or choose/make a dummy provider/option
            self.self_state = VPSState(provider="linevast", option="Basic")
            self.init_qtable(providers)
            self.init_alpha_and_beta()
            self.create_initial_tree()
            self.write_dictionary()
        else:
            with open(filename) as json_file:
                data_encoded = json.load(json_file)
                data = jsonpickle.decode(data_encoded)
                self.qtable = data['qtable']
                self.alphatable = data['alpha']
                self.betatable = data['beta']
                self.providers_offers = data['providers_offers']
                self.self_state = data['self_state']
                self.tree = data['tree']

    def init_qtable(self, providers):
        """
        Initializes the qtable with starting values.
        """
        self.init_providers_offers(providers)
        # self.qtable = {k: i for i, k in enumerate(self.providers_offers)} # if all initialized to 0
        self.qtable = {}
        for provider_offer in self.providers_offers:
            # TODO: find new begin value or set it to 0 use above line
            # TODO: estimate the amount of MB tokens / usd or eur vps / day
            self.qtable[self.get_ID(provider_offer)] = 0

    def init_alpha_and_beta(self):
        """
        Initialize the alpha and beta tables with their respective starting values.
        """
        self.alphatable = {i: self.start_alpha for i in self.providers_offers}
        self.betatable = {i: self.start_beta for i in self.providers_offers}

    def init_providers_offers(self, providers):
        for i, id in enumerate(providers):
            options = cloudomate_controller.options(providers[id])
            for i, option in enumerate(options):
                element = ProviderOffer(provider_name=providers[id].get_metadata()[0], name=str(option.name),
                                        bandwidth=option.bandwidth, price=option.price, memory=option.memory)
                self.providers_offers.append(element)

    def create_initial_tree(self):
        self.tree = plebnet_settings.get_instance().irc_nick()

    @staticmethod
    def get_ID(provider_offer):
        return str(provider_offer.provider_name).lower() + "_" + str(provider_offer.name).lower()

    # def get_ID_from_state(self):
    #     return str(self.self_state.provider).lower() + "_" + str(self.self_state.option).lower()
    #
    # # def choose_option(self, providers):
    #     lambd = 1 - 1 / (self.get_no_replications() + 3)
    #     num = random.expovariate(lambd)
    #     num = int(math.floor(num))
    #
    #     if num > len(self.qtable[self.get_ID_from_state()]) - 1:
    #         num = len(self.qtable[self.get_ID_from_state()]) - 1
    #
    #     return self.choose_k_option(providers, num)
    #
    # def choose_k_option(self, providers, num):
    #     candidate = {"option": {}, "option_name": "", "provider_name": "", "score": -self.INFINITY,
    #                  "price": self.INFINITY,
    #                  "currency": "USD"}
    #
    #     score = self.get_kth_score(providers, num)
    #
    #     for i, offer_name in enumerate(self.qtable):
    #         if self.qtable[self.get_ID_from_state()][offer_name] == score and self.find_provider(
    #                 offer_name) in providers:
    #             candidate["score"] = self.qtable[self.get_ID_from_state()][offer_name]
    #             provider = self.find_provider(offer_name)
    #             candidate["provider_name"] = provider
    #             candidate["option_name"] = self.find_offer(offer_name, provider)
    #
    #     # TODO: Handle an edge case when cloudomate fails and options returns an empty array
    #     options = cloudomate_controller.options(providers[candidate["provider_name"]])
    #
    #     for i, option in enumerate(options):
    #         if option.name == candidate["option_name"]:
    #             candidate["option"] = option
    #             candidate["price"] = option.price
    #
    #     return candidate
    #
    # def get_kth_score(self, providers, num):
    #     to_choose_scores = []
    #     for i, offername in enumerate(self.qtable):
    #         if self.find_provider(offername) in providers:
    #             elem = {"score": self.qtable[self.get_ID_from_state()][offername], "id": offername}
    #             to_choose_scores.append(elem)
    #     to_choose_scores.sort(key=lambda x: x["score"], reverse=True)
    #     return to_choose_scores[num]["score"]
    #
    # def find_provider(self, offer_name):
    #     for offer in self.providers_offers:
    #         if self.get_ID(offer) == offer_name:
    #             return offer.provider_name.lower()
    #     raise ValueError("Can't find provider for " + offer_name)
    #
    # def find_offer(self, offer_name, provider):
    #     for offer in self.providers_offers:
    #         if self.get_ID(offer) == offer_name and provider.lower() == offer.provider_name.lower():
    #             return offer.name
    #     raise ValueError("Can't find offer for " + offer_name)
    #
    # def get_no_replications(self):
    #     return len(self.tree.split("."))


class ProviderOffer:
    UNLIMITED_BANDWIDTH = 10

    def __init__(self, provider_name="", name="", bandwidth="", price=0, memory=0):
        self.provider_name = provider_name
        self.name = name
        self.price = price
        self.memory = memory
        try:
            bandwidth = float(bandwidth)
            if bandwidth < sys.maxsize:
                self.bandwidth = bandwidth
            else:
                self.bandwidth = self.UNLIMITED_BANDWIDTH
        except:
            self.bandwidth = self.UNLIMITED_BANDWIDTH


class VPSState:
    def __init__(self, provider="", option=""):
        self.provider = provider
        self.option = option

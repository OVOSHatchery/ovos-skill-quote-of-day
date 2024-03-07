from os.path import join, dirname
from datetime import datetime, timedelta
import requests
from ovos_workshop.decorators import resting_screen_handler, intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills.ovos import OVOSSkill


class QuoteOfDaySkill(OVOSSkill):
    categories = ['inspire', 'management', 'sports', 'life', 'funny',
                  'love', 'art', 'students']

    def initialize(self):
        if "default_category" not in self.settings:
            self.settings["default_category"] = "random"

    def update_quote(self, category="random"):
        if category not in self.settings:
            self.settings[category] = {}
        try:
            today = datetime.now().replace(hour=12, second=0, minute=0,
                                           microsecond=0)
            if not self.settings[category].get("ts"):
                self.settings[category]["ts"] = (today - timedelta(days=1)).timestamp()
            if today.timestamp() != self.settings[category]["ts"] or not \
                    self.settings[category].get('quote'):
                data = self.get_quote_of_the_day(category)
                for k in data:
                    self.settings[category][k] = data[k]
                # {'quote': 'As a leader... I have always endeavored to listen to what each and every person in a discussion had to say before venturing my own opinion. Oftentimes, my own opinion will simply represent a con-sensus of what I heard in the discussion. I always remember the axiom: a leader is like a shepherd. He stays behind the flock, letting the most nimble go out ahead, whereupon the others follow, not realizing that all along they are being directed from behind.',
                # 'length': '454',
                # 'author': 'Nelson Mandela',
                # 'tags': ['leadership', 'management', 'opinions'],
                # 'category': 'management',
                # 'language': 'en',
                # 'date': '2020-06-13',
                # 'permalink': 'https://theysaidso.com/quote/nelson-mandela-as-a-leader-i-have-always-endeavored-to-listen-to-what-each-and-e',
                # 'id': 'HvpmrpvTJpH0OTz4b_sqbAeF',
                # 'background': 'https://theysaidso.com/img/qod/qod-management.jpg',
                # 'title': 'Management Quote of the day'}
                qod = data["'quote'"]
                if self.lang.split("-")[0].lower() != \
                        data["lang"].split("-")[0].lower():
                    qod = self.translator.translate(qod, self.lang)
                    self.settings[category]['quote'] = qod

                self.settings[category]["ts"] = today.timestamp()
        except Exception as e:
            self.log.exception(e)
        self.gui['quote'] = self.settings[category]['quote']
        self.gui['author'] = self.settings[category]['author']
        self.set_context("WHO", self.settings[category]['author'])  # enable "who said that" intent

    @resting_screen_handler("QuoteOfDay")
    def idle(self, message):
        self.update_quote(self.settings["default_category"])
        self.gui.show_page('idle.qml')

    def get_quote_of_the_day(self, category="random"):
        key = self.settings.get("key", "o3FQPFaAp4wCnvLlmXzk3UEyi4yAnHWSlUWhn9x0")
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {key}'
        }
        url = 'https://quotes.rest/qod'
        if category == "random":
            response = requests.get(url, headers=headers).json()
        else:
            assert category in self.categories
            response = requests.get(url, headers=headers,
                                    params={"category": category}).json()
        self.log.debug("Quotes Api Response: " + str(response))
        return response['contents']['quotes'][0]

    def speak_quote(self, category):
        self.update_quote(category)
        self.gui.show_image(self.settings[category]['background'],
                            caption=self.settings[category]['quote'])
        self.speak(self.settings[category]['quote'], wait=True)
        self.gui.clear()

    @intent_handler(IntentBuilder("QuoteOfTheDayIntent")
                    .require("quote_of_day"))
    def handle_quote_of_day(self, message):
        self.speak_quote(self.settings["default_category"])

    @intent_handler(IntentBuilder("LoveQuoteOfTheDayIntent")
                    .require("quote_of_day").require("love"))
    def handle_love_quote_of_day(self, message):
        self.speak_quote("love")

    @intent_handler(IntentBuilder("InspireQuoteOfTheDayIntent")
                    .require("quote_of_day").require("inspire"))
    def handle_inspire_quote_of_day(self, message):
        self.speak_quote("inspire")

    @intent_handler(IntentBuilder("ArtQuoteOfTheDayIntent")
                    .require("quote_of_day").require("art"))
    def handle_art_quote_of_day(self, message):
        self.speak_quote("art")

    @intent_handler(IntentBuilder("FunnyQuoteOfTheDayIntent")
                    .require("quote_of_day").require("funny"))
    def handle_funny_quote_of_day(self, message):
        self.speak_quote("funny")

    @intent_handler(IntentBuilder("LifeQuoteOfTheDayIntent")
                    .require("quote_of_day").require("life"))
    def handle_life_quote_of_day(self, message):
        self.speak_quote("life")

    @intent_handler(IntentBuilder("ManagementQuoteOfTheDayIntent")
                    .require("quote_of_day").require("management"))
    def handle_management_quote_of_day(self, message):
        self.speak_quote("management")

    @intent_handler(IntentBuilder("SportsQuoteOfTheDayIntent")
                    .require("quote_of_day").require("sports"))
    def handle_sports_quote_of_day(self, message):
        self.speak_quote("sports")

    @intent_handler(IntentBuilder("LoveQuoteOfTheDayIntent")
                    .require("quote_of_day").require("students"))
    def handle_students_quote_of_day(self, message):
        self.speak_quote("students")

    @intent_handler(IntentBuilder("WhoSaidIntent")
                    .require("who").require("said_that").require("WHO"))
    def handle_who_said(self, message):
        author = message.data["WHO"]
        self.speak(author, wait=True)

    @intent_handler("trustworthy.intent")
    def handle_trustworthy(self, message):
        self.speak_dialog("no_idea")

    @intent_handler("source.intent")
    def handle_source(self, message):
        self.gui.show_image(join(dirname(__file__), "logo.png"),
                            caption="Take all info with a grain of salt",
                            fill='PreserveAspectFit')
        self.speak_dialog("theysaidso", wait=True)
        self.gui.clear()


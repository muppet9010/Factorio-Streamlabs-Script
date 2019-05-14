import json as Json
import os as Os
import requests as Requests
import datetime as Datetime


class Currency():
    def __init__(self, state):
        self.Logging = state.Logging
        self.State = state
        self.rates = {}
        self.cacheFileName = "currency data cache.json"

    def GetRates(self):
        if len(self.rates) > 0:
            return True
        if Os.path.isfile(self.cacheFileName):
            self.Logging.DebugLog(
                "Trying to get currancy rates from cache file")
            with open(self.cacheFileName, "r") as file:
                data = Json.load(file)
            file.closed
            cacheDateTime = Datetime.date.fromtimestamp(data["timestamp"])
            currentDateTime = Datetime.date.fromtimestamp(
                Datetime.datetime.utcnow().timestamp())
            if currentDateTime <= cacheDateTime:
                for name, rate in data["quotes"].items():
                    currency = name[3:]
                    self.rates[currency] = rate
                if len(self.rates) > 0:
                    self.Logging.DebugLog(
                        "Got currency rates from cache file")
                    return True

        self._SourceRateData()
        if len(self.rates) > 0:
            self.Logging.DebugLog("Got currency rates from website")
            return True
        else:
            self.Logging.DebugLog(
                "Failed to get any currency rates from website")
            return False

    def _SourceRateData(self):
        self.Logging.DebugLog("Sourcing currency rates from website")
        url = "http://www.apilayer.net/api/live"
        params = {"access_key": self.State.Config.GetSetting(
            "Currency ApiLayerAccessKey")}
        request = Requests.get(url=url, params=params)
        response = request.json()
        if not response["success"]:
            self.State.RecordActivity(
                self.State.Translations.currentTexts["Currency WebsiteDownloadFailed"])
            return False
        with open(self.cacheFileName, "w") as file:
            file.write(Json.dumps(response))
        file.closed
        for name, rate in response["quotes"].items():
            currency = name[3:]
            self.rates[currency] = rate

    def GetNormalisedValue(self, currency, amount):
        return round(amount / self.rates[currency], 2)

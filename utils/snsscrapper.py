from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json
from datetime import date
from datetime import datetime, timedelta
from dotenv import dotenv_values

envConfig = dotenv_values(".env")


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target, configurations):
        if (target['targetType'] == 'keywords'):
            if len(target['tweets']) == 0:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        if counter > 100:
                            break
                        tweets.append(json.loads(tweet.json()))
                    if len(tweets) > 0:
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}})
                        # print(f"First Entry !!! Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        # print(">>> Scheduled!!! No new tweets were found for  " + target['targetType'] + " against keyword " + keyword)
                        return None

            else:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        if counter > 100:
                            break
                        exist = list(filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))
                        if not exist:
                            tweets.append(json.loads(tweet.json()))
                    if len(tweets) > 0:
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        update = {'$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        # print(f"Scheduled : Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        # print(">>> Scheduled!!! No new tweets were found for  " + target['targetType'] + " against keyword " + keyword)
                        return None

        elif (target['targetType'] == 'twitter-user'):
            try:
                scrappedTweets = []
                inlcudeTimeframe = int(envConfig["SNS_CONFIG_INCLUDE_TIMEFRAME"]),
                targetUsername = target['targets'][0].strip()
                searchQuery = ''
                for counter, inKeyword in enumerate(configurations['inKeywords']):
                    if (counter > 0):
                        searchQuery += ' OR '+inKeyword.strip()
                    else:
                        searchQuery += ''+inKeyword.strip()
                startDate = str(date.today()-timedelta(days=365))
                endDate = str(date.today())
                if inlcudeTimeframe:
                    searchQuery = "from:"+targetUsername+" "+searchQuery+" since:"+startDate
                else:
                    searchQuery = "from:"+targetUsername+" "+searchQuery
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                # print(searchQuery)
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

                if len(target['tweets']) == 0:
                    for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(searchQuery).get_items()):
                        # print(counter, tweet.rawContent)
                        scrappedTweets.append(json.loads(tweet.json()))
                    if len(scrappedTweets) > 0:
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': scrappedTweets}}})
                        # print(f"First Entry !!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + targetUsername)
                        return scrappedTweets
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        # print("IF NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + targetUsername)
                        return None

                else:
                    for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(searchQuery).get_items()):
                        # print(counter, tweet.rawContent)
                        scrappedTweets.append(json.loads(tweet.json()))
                    if len(scrappedTweets) > 0:
                        if (len(scrappedTweets) > len(target['tweets'])):
                            newScrappedTweets = list(filter(lambda x: len(list(filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrappedTweets))
                            if len(newScrappedTweets) > 0:
                                result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': newScrappedTweets}}})
                                # print(f"Scheduled!!! Matched {result.matched_count} documents for  " + target['targetType'] + " against username " + targetUsername)
                                return newScrappedTweets
                            else:
                                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                                # print("ELSE NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + targetUsername)
                                return None
                        else:
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})

                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        # print("ELSE NO TWEETS FOUND!!!  " + target['targetType'] + " against username " + targetUsername)

            except Exception as e:
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                # print(e)
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                return None

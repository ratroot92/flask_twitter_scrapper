from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json
from datetime import date
from datetime import datetime, timedelta


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target, configuration):
        if (target['target_type'] == 'keywords'):
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
                        print(f"First Entry !!! Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['target_type'] + " against keyword " + keyword)
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
                        print(f"Scheduled : Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['target_type'] + " against keyword " + keyword)
                        return None

        elif (target['target_type'] == 'twitter-user'):
            try:
                searchQuery = ''
                for counter, inKeword in enumerate(configuration['in_keywords']):
                    if (counter > 0):
                        searchQuery += ' OR '+inKeword.strip()
                    else:
                        searchQuery += ''+inKeword.strip()
                startDate = str(date.today()-timedelta(days=365))
                endDate = str(date.today())
                searchQuery = searchQuery+" since:"+startDate+" until:"+endDate
                if len(target['tweets']) == 0:
                    for username in target['targets']:
                        try:
                            scrappedTweets = []
                            query = "from:"+username + " " + searchQuery
                            for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                                # if counter > 100:
                                #     break
                                print(tweet.rawContent)
                                scrappedTweets.append(json.loads(tweet.json()))
                            print(">>>>>>> IF query", query)
                            print(">>>>>>> IF queryResults New ", len(scrappedTweets), " tweets  found...")
                            if len(scrappedTweets) > 0:
                                result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': scrappedTweets}}})
                                print(f"First Entry !!! Matched {result.matched_count} documents for  " + target['target_type'] + " against username " + username)
                                return None
                            else:
                                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                                print("IF NO TWEETS FOUND!!!  " + target['target_type'] + " against username " + username)
                                return None
                        except:
                            print("Something went wrong!!! Resetting target status")
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})

                else:
                    for username in target['targets']:
                        try:
                            scrappedTweets = []
                            startDate = str(date.today()-timedelta(days=365))
                            endDate = str(date.today())
                            query = "from:"+username + " " + searchQuery
                            for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                                # if counter > 100:
                                #     break
                                print(tweet.rawContent)
                                scrappedTweets.append(json.loads(tweet.json()))
                            print(">>>>>>> ELSE query", query)
                            print(">>>>>>> ELSE queryResults New ", len(scrappedTweets), " tweets  found...")
                            if len(scrappedTweets) > 0:
                                if (len(scrappedTweets) > len(target['tweets'])):
                                    newScrappedTweets = list(filter(lambda x: len(list(filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrappedTweets))
                                    if len(newScrappedTweets) > 0:
                                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': newScrappedTweets}}})
                                        print(f"Scheduled!!! Matched {result.matched_count} documents for  " + target['target_type'] + " against username " + username)
                                        return newScrappedTweets
                                    else:
                                        return None
                            else:
                                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                                print("ELSE NO TWEETS FOUND!!!  " + target['target_type'] + " against username " + username)
                            return None
                        except:
                            print("Something went wrong!!! Resetting target status")
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})

            except Exception as e:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(e)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                return None

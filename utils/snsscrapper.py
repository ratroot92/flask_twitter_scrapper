from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json
from datetime import date
from datetime import datetime, timedelta
from dotenv import dotenv_values

env_config = dotenv_values(".env")


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target):

        if (target['target_type'] == 'keywords'):
            if len(target['tweets']) == 0:
                for keyword in target['targets']:
                    tweets = []
                    sns_scrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(sns_scrapper.get_items()):
                        if counter > 100:
                            break
                        tweets.append(json.loads(tweet.json()))
                    if len(tweets) > 0:
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                                       '$set': {'status': 0}, '$push': {'tweets': {'$each': tweets}}})
                        print(f"First Entry !!! Matched {result.matched_count} documents.")
                        return None
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                              '$set': {'status': 0}})
                        print(">>> Scheduled!!! No new tweets were found for  " + target['target_type'] + " against keyword " + keyword)
                        return None

            else:
                for keyword in target['targets']:
                    tweets = []
                    sns_scrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(sns_scrapper.get_items()):
                        if counter > 100:
                            break
                        exist = list(
                            filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))
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
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                              '$set': {'status': 0}})
                        # print(">>> Scheduled!!! No new tweets were found for  " + target['target_type'] + " against keyword " + keyword)
                        return None

        elif (target['target_type'] == 'twitter-user'):
            try:
                scrapped_tweets = []
                inlcude_timeframe = int(env_config["SNS_CONFIG_INCLUDE_TIMEFRAME"]),
                target_username = target['targets'][0].strip()
                search_query = ''
                for counter, in_keyword in enumerate(target['configuration']['in_keywords']):
                    if (counter > 0):
                        search_query += ' OR ' + in_keyword.strip()
                    else:
                        search_query += '' + in_keyword.strip()
                start_date = str(date.today() - timedelta(days=365))
                end_date = str(date.today())
                if inlcude_timeframe:
                    search_query = "from:" + target_username + " " + search_query + " since:" + start_date
                else:
                    search_query = "from:" + target_username + " " + search_query
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(search_query)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

                if len(target['tweets']) == 0:
                    for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
                        # print(counter, tweet.rawContent)
                        scrapped_tweets.append(json.loads(tweet.json()))
                    if len(scrapped_tweets) > 0:
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}, '$push': {'tweets': {'$each': scrapped_tweets}}})
                        print(f"First Entry !!! Matched {result.matched_count} documents for  " + target['target_type'] + " against username " + target_username)
                        return scrapped_tweets
                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                        print("IF NO TWEETS FOUND!!!  " + target['target_type'] + " against username " + target_username)
                        return None

                else:
                    for counter, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
                        print(counter, tweet.rawContent)
                        scrapped_tweets.append(json.loads(tweet.json()))
                    if len(scrapped_tweets) > 0:
                        if (len(scrapped_tweets) > len(target['tweets'])):
                            new_scrapped_tweets = list(filter(lambda x: len(list(
                                filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrapped_tweets))
                            if len(new_scrapped_tweets) > 0:
                                result = db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                                               '$set': {'status': 0}, '$push': {'tweets': {'$each': new_scrapped_tweets}}})
                                print(f"Scheduled!!! Matched {result.matched_count} documents for  " + target['target_type'] + " against username " + target_username)
                                return new_scrapped_tweets
                            else:
                                db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                                      '$set': {'status': 0}})
                                print("ELSE NO TWEETS FOUND!!!  " + target['target_type'] + " against username " + target_username)
                                return None
                        else:
                            db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                                  '$set': {'status': 0}})

                    else:
                        db.targets.update_one({'_id': ObjectId(target['_id'])}, {
                                              '$set': {'status': 0}})
                        print("ELSE NO TWEETS FOUND!!!  " + target['target_type'] + " against username " + target_username)

            except Exception as e:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(e)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                db.targets.update_one({'_id': ObjectId(target['_id'])}, {'$set': {'status': 0}})
                return None

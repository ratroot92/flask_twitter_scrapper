from pprint import pprint
from bson.objectid import ObjectId
import snscrape.modules.twitter as sntwitter
from config.db import db
import json
from javascript import require, globalThis


class Scrapper:
    def __init__(self) -> None:
        self.kewordsArr = ['love']
        pass

    @staticmethod
    def scrapKeywords(target):
        if (target['targetType'] == 'keywords'):
            if len(target['tweets']) == 0:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        # if counter >= int(target['limit']):
                        #     break
                        tweets.append({'keyword': keyword, 'date': tweet.date, 'id': tweet.id, 'rawContent': tweet.rawContent, 'username': tweet.user.username})
                    if len(tweets) > 0:
                        update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        print(f"First Entry !!! Matched {result.matched_count} documents.")
                        print(f"First Entry !!! Modified {result.modified_count} documents.")
                        return None
                    else:
                        print(">>> First Entry !!! No new tweets were found for "+exist['_id']+" " + exist['targetType'])
                        return None

            else:
                for keyword in target['targets']:
                    tweets = []
                    snsScrapper = sntwitter.TwitterSearchScraper(keyword)
                    for counter, tweet in enumerate(snsScrapper.get_items()):
                        # if counter >= int(target['limit']):
                        #     break
                        exist = list(filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))
                        if not exist:
                            tweets.append({'keyword': keyword, 'date': tweet.date, 'id': tweet.id, 'rawContent': tweet.rawContent, 'username': tweet.user.username})
                    if len(tweets) > 0:
                        update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
                        result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                        print(f"Scheduled : Matched {result.matched_count} documents.")
                        print(f"Scheduled : Modified {result.modified_count} documents.")
                        return None
                    else:
                        print(">>> Scheduled!!! No new tweets were found for "+target['_id']+" " + target['targetType'] + " against keyword " + keyword)
                        return None

        elif (target['targetType'] == 'twitter-user'):
            try:
                if target['status'] == 0:
                    for username in target['targets']:
                        tweets = []
                        snsScrapper = sntwitter.TwitterUserScraper(username)
                        for counter, tweet in enumerate(snsScrapper.get_items()):
                            if 'love' in tweet.rawContent:
                                tweets.append(json.loads(tweet.json()))
                        if len(tweets) > 0:
                            update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
                            result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                            print(f"First Entry !!! Matched {result.matched_count} documents for "+target['_id']+" " + target['targetType'] + " against username " + username)
                            print(f"First Entry !!! Modified {result.modified_count} documents for "+target['_id']+" " + target['targetType'] + " against username " + username)
                            return None
                        else:
                            print(">>> First Entry !!! No new tweets were found for "+target['_id']+" " + target['targetType'] + " against username " + username)
                            return None
                else:
                    for username in target['targets']:
                        scrappedTweets = []
                        snsScrapper = sntwitter.TwitterUserScraper(username)
                        for counter, tweet in enumerate(snsScrapper.get_items()):
                            if 'love' in tweet.rawContent:
                                scrappedTweets.append(json.loads(tweet.json()))
                        if len(scrappedTweets) > 0:
                            if (len(scrappedTweets) > len(target['tweets'])):
                                newScrappedTweets = list(filter(lambda x: len(list(filter(lambda y: y['id'] == x['id'], target['tweets']))) == 0, scrappedTweets))
                                if len(newScrappedTweets) > 0:
                                    update = {'$push': {'tweets': {'$each': newScrappedTweets}}}
                                    result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
                                    print(f"Scheduled!!! Matched {result.matched_count} documents for "+target['_id']+" " + target['targetType'] + " against username " + username)
                                    print(f"Scheduled!!! Modified {result.modified_count} documents for "+target['_id']+" " + target['targetType'] + " against username " + username)
                                    return newScrappedTweets
                                else:
                                    return None

                        else:
                            print(">>> First Entry !!! No new tweets were found for "+target['_id']+" " + target['targetType'] + " against username " + username)
                            return None
            except Exception as e:
                print(e)
                return None
            # else:
            #     for username in target['targets']:
            #         tweets = []
            #         snsScrapper = sntwitter.TwitterUserScraper(username)
            #         for counter, tweet in enumerate(snsScrapper.get_items()):
            #             if counter >= int(target['limit']):
            #                 break
            #             exist = list(filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))
            #             if not exist:
            #                 tweets.append({'username': username, 'date': tweet.date, 'id': tweet.id, 'rawContent': tweet.rawContent, 'username': tweet.user.username})
            #         if len(tweets) > 0:
            #             update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
            #             result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
            #             update = {'$set': {'status': 1}, '$push': {'tweets': {'$each': tweets}}}
            #             result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)
            #             print(f"Scheduled : Matched {result.matched_count} documents.")
            #             print(f"Scheduled : Modified {result.modified_count} documents.")
            #         else:
            #             print(">>> Scheduled!!! No new tweets were found for "+target['_id']+" " + target['targetType'] + " against username " + username)
            # except Exception as e:
            #     print(e)
            # update = {'$set': {'status': 2}, }
            # result = db.targets.update_one({'_id': ObjectId(target['_id'])}, update)

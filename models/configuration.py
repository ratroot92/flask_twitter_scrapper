from config.db import db


class TargetConfiguration():

    def __init__(self, likesCount, retweetCount, location, viewCount, inKeywords, outKeywords, user):
        self.likeCount = likesCount or 1
        self.retweetCount = retweetCount or 1
        self.location = location
        self.viewCount = viewCount or 1
        self.inKeywords = inKeywords or []
        self.outKeywords = outKeywords or []
        self.user = user

    def __str__(self):
        return f" >>>  TargetConfig({self.likeCount},{self.retweetCount},{self.location})"

    def __repr__(self):
        rep = 'TargetConfig(' + self.likeCount + ',' + str(self.retweetCount) + ')'
        return rep

    @staticmethod
    def TargetConfigExist(query):
        target = db.target_configurations.find_one({'likeCount': query['likeCount']})
        if target:
            target["_id"] = str(target['_id'])
            target["location"] = str(target['location'])
            return target
        else:
            return False

    @staticmethod
    def getTargetConfig(authUser):
        data = []
        retweetCount = db.target_configurations.find({'location': authUser['_id']})
        for target in retweetCount:
            target['_id'] = str(target['_id'])
            target['location'] = str(target['location'])
            data.append(target)
        return data

    def serialize(self):
        return {
            '_id': str(self._id),
            'likeCount': self.likeCount,
            'retweetCount': self.retweetCount,
            'location': self.location,
            'viewCount': self.viewCount,
            'inKeywords': self.inKeywords,
            'outKeywords': self.outKeywords,




        }

    def toDictionary(self):
        return {
            'likeCount': self.likesCount,
            'retweetCount': self.retweetCount,
            'location': self.location,
            'viewCount': self.viewCount,
            'inKeywords': self.inKeywords,
            'outKeywords': self.outKeywords,




        }

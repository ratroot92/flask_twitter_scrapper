from config.db import db


class Confgiuration():

    def __init__(self, likeCount, retweetCount, viewCount, inKeywords, outKeywords, user):
        self.likeCount = likeCount
        self.retweetCount = retweetCount
        self.viewCount = viewCount
        self.inKeywords = inKeywords
        self.outKeywords = outKeywords
        self.user = user

    def __str__(self):
        return f" >>>  Confgiuration({self.likeCount},{self.retweetCount})"

    def __repr__(self):
        rep = 'Confgiuration(' + self.likeCount + ',' + \
            str(self.retweetCount) + ')'
        return rep

    def serialize(self):
        return {
            '_id': str(self._id),
            'likeCount': self.likeCount,
            'retweetCount': self.retweetCount,
            'viewCount': self.viewCount,
            'inKeywords': self.inKeywords,
            'outKeywords': self.outKeywords,
            'user': self.user,





        }

    def toDictionary(self):
        return {
            'likeCount': self.likeCount,
            'retweetCount': self.retweetCount,
            'viewCount': self.viewCount,
            'inKeywords': self.inKeywords,
            'outKeywords': self.outKeywords,
            'user': self.user,

        }

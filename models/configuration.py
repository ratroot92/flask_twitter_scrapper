from config.db import db


class Confgiuration():

    def __init__(self, like_count, retweet_count, view_count, in_keywords, out_keywords, user):
        self.like_count = like_count
        self.retweet_count = retweet_count
        self.view_count = view_count
        self.in_keywords = in_keywords
        self.out_keywords = out_keywords
        self.user = user

    def __str__(self):
        return f" >>>  Confgiuration({self.like_count},{self.retweet_count})"

    def __repr__(self):
        rep = 'Confgiuration(' + self.like_count + ',' + \
            str(self.retweet_count) + ')'
        return rep

    def serialize(self):
        return {
            '_id': str(self._id),
            'like_count': self.like_count,
            'retweet_count': self.retweet_count,
            'view_count': self.view_count,
            'in_keywords': self.in_keywords,
            'out_keywords': self.out_keywords,
            'user': self.user,





        }

    def toDictionary(self):
        return {
            'like_count': self.like_count,
            'retweet_count': self.retweet_count,
            'view_count': self.view_count,
            'in_keywords': self.in_keywords,
            'out_keywords': self.out_keywords,
            'user': self.user,

        }

from config.db import db


class Target():

    def __init__(self, target_type, targets, user, limit, configuration, tweets=[], status=0, ):

        self.target_type = target_type
        self.targets = targets
        self.user = user
        self.limit = limit or 10
        self.tweets = tweets or []
        self.status = status or 0
        self.configuration = {
            'like_count': configuration['like_count'],
            'retweet_count': configuration['retweet_count'],
            'view_count': configuration['view_count'],
            'in_keywords': configuration['in_keywords'],
            'out_keywords': configuration['out_keywords'],
        }

    def __str__(self):
        return f" >>>  Target({self.target_type},{self.targets},{self.user})"

    def __repr__(self):
        rep = 'Target(' + self.target_type + ',' + str(self.targets) + ')'
        return rep

    @staticmethod
    def TargetExist(query):
        target = db.targets.find_one({'target_type': query['target_type']})
        if target:
            target["_id"] = str(target['_id'])
            target["user"] = str(target['user'])
            return target
        else:
            return False

    @staticmethod
    def GetUserTargets(authUser):
        data = []
        targets = db.targets.find({'user': authUser['_id']})
        for target in targets:
            target['_id'] = str(target['_id'])
            target['user'] = str(target['user'])
            data.append(target)
        return data

    def serialize(self):
        return {
            '_id': str(self._id),
            'target_type': self.target_type,
            'targets': self.targets,
            'user': self.user,
            'limit': self.limit,
            'tweets': self.tweets,
            'status': self.status,
            'configuration': {
                'like_count': self.configuration['like_count'],
                'retweet_count': self.configuration['retweet_count'],
                'view_count': self.configuration['view_count'],
                'in_keywords': self.configuration['in_keywords'],
                'out_keywords': self.configuration['out_keywords'],
            }



        }

    def toDictionary(self):
        return {
            # '_id': str(self._id),
            'target_type': self.target_type,
            'targets': self.targets,
            'user': self.user,
            'limit': self.limit,
            'tweets': self.tweets,
            'status': self.status,
            'configuration': {
                'like_count': self.configuration['like_count'],
                'retweet_count': self.configuration['retweet_count'],
                'view_count': self.configuration['view_count'],
                'in_keywords': self.configuration['in_keywords'],
                'out_keywords': self.configuration['out_keywords'],
            }



        }

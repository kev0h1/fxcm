class AbstractUnitOfWork:
    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError


class MongoUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

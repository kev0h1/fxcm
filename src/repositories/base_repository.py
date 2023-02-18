class BaseRepository:
    def add(self, obj):
        """Add an object"""
        obj.save()
        return obj

class BaseRepository:
    def save(self, obj):
        """Add an object"""
        obj.save()
        return obj

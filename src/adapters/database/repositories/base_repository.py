class BaseRepository:
    async def save(self, obj):
        """Add an object"""
        obj.save()
        return obj

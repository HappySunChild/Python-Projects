from __future__ import annotations

class BaseData:
	id = None
	
	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}>'
	
	def __eq__(self, value: object) -> bool:
		if isinstance(value, BaseData):
			return self.id == value.id
		
		return False
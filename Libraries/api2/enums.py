from enum import Enum, IntEnum

class PresenceType(IntEnum):
	offline = 0
	online = 1
	in_game = 2
	in_studio = 3
	invisible = 4

class SortOrder(Enum):
	Ascending = 'Asc'
	Descending = 'Desc'

class AssetType(Enum):
	Image = 1
	Decal = 13
	Video = 62
	Audio = 3
	FontFamily = 73
	
	Mesh = 4
	MeshPart = 40
	Lua = 5
	Place = 9
	Model = 10
	Animation = 24
	Plugin = 38
	
	Gear = 19
	Badge = 21
	GamePass = 34
	
	DynamicHead = 79
	Head = 17
	Face = 18
	Torso = 27
	RightArm = 28
	LeftArm = 29
	LeftLeg = 30
	RightLeg = 31
	Package = 32
	
	HairAccessory = 41
	FaceAccessory = 42
	NeckAccessory = 43
	ShoulderAccessory = 44
	FrontAccessory = 45
	BackAccessory = 46
	WaistAccessory = 47
	EarAccessory = 57
	EyeAccessory = 58
	EyebrowAccessory = 76
	EyelashAccessory = 77
	
	TShirtAccessory = 64
	ShirtAccessory = 65
	PantsAccessory = 66
	JacketAccessory = 67
	SweaterAccessory = 68
	ShortsAccessory = 69	
	LeftShoeAccessory = 70
	RightShoeAccessory = 71
	DressSkirtAccessory = 72
	
	ClimbAnimation = 48
	DeathAnimation = 49 #?
	FallAnimation = 50
	IdleAnimation = 51
	JumpAnimation = 52
	RunAnimation = 53
	SwimAnimation = 54
	WalkAnimation = 55
	PoseAnimation = 56
	EmoteAnimation = 61
	MoodAnimation = 78
	
	Hat = 8
	Shirt = 11
	Pants = 12
	TShirt = 2
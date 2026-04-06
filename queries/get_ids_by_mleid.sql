select
	mlep.mleid as "MLEID",
	mlep.discord_id as "Discord ID",
	u.id as "Sprocket User ID",
	m.id as "Sprocket Member ID",
	p.id as "Sprocket Player ID",
	mlep.id as "MLEDB Player ID"
from
	sprocket."user" u
inner join sprocket.member m on
	m."userId" = u.id
inner join sprocket.player p on
	p."memberId" = m.id
inner join sprocket.user_authentication_account uaa on
	uaa."userId" = u.id
inner join mledb.player mlep on
	mlep.discord_id = uaa."accountId"
where
	mlep.mleid = 14925

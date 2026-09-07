-- Seed sprocket.roster_role with the eight standard player slot codes (PLAYERA–PLAYERH)
-- used by Sprocket NCP team-role import (see slotLetterToRole / Role enum in sprocket).
--
-- Roster roles are defined per game_skill_group (game + skill tier + organization), not per team.
-- Every team in that skill group shares these role rows; roster_slot links a team to a role.
--
-- Safe to re-run: skips rows that already exist for the same skill group and code.

INSERT INTO sprocket.roster_role (code, description, "gameId", "skillGroupId", "organizationId")
SELECT
    r.code,
    r.description,
    gsg."gameId",
    gsg.id,
    gsg."organizationId"
FROM sprocket.game_skill_group gsg
CROSS JOIN (
    VALUES
        ('PLAYERA', 'Player slot A'),
        ('PLAYERB', 'Player slot B'),
        ('PLAYERC', 'Player slot C'),
        ('PLAYERD', 'Player slot D'),
        ('PLAYERE', 'Player slot E'),
        ('PLAYERF', 'Player slot F'),
        ('PLAYERG', 'Player slot G'),
        ('PLAYERH', 'Player slot H')
) AS r (code, description)
WHERE gsg."deletedAt" IS NULL
  AND gsg."gameId" IS NOT NULL
  AND gsg."organizationId" IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM sprocket.roster_role rr
      WHERE rr."skillGroupId" = gsg.id
        AND rr.code = r.code
        AND rr."deletedAt" IS NULL
  );

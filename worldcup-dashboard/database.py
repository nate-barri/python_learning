import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

# Build the connection URL from your .env
DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, echo=False)
Base = declarative_base()


# --- Table 1: Teams ---
class Team(Base):
    __tablename__ = "teams"

    team_id    = Column(Integer, primary_key=True)
    name       = Column(String(100), nullable=False)
    code       = Column(String(10))
    country    = Column(String(100))
    group_name = Column(String(10))   # e.g. "Group A"
    logo_url   = Column(String(255))

    players  = relationship("Player",  back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")


# --- Table 2: Matches ---
class Match(Base):
    __tablename__ = "matches"

    fixture_id   = Column(Integer, primary_key=True)
    date         = Column(DateTime)
    venue        = Column(String(150))
    city         = Column(String(100))
    status       = Column(String(10))   # NS, 1H, HT, 2H, FT, etc.
    elapsed      = Column(Integer)      # minute of match
    round        = Column(String(50))   # "Group Stage - 1", "Quarter-finals", etc.
    home_team_id = Column(Integer, ForeignKey("teams.team_id"))
    away_team_id = Column(Integer, ForeignKey("teams.team_id"))
    home_goals   = Column(Integer)
    away_goals   = Column(Integer)

    home_team  = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team  = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    events     = relationship("Event",    back_populates="match")
    standings  = relationship("Standing", back_populates="match")


# --- Table 3: Events (goals, cards, subs) ---
class Event(Base):
    __tablename__ = "events"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id   = Column(Integer, ForeignKey("matches.fixture_id"))
    minute       = Column(Integer)
    extra_minute = Column(Integer)    # for 90+4 style goals
    team_id      = Column(Integer, ForeignKey("teams.team_id"))
    player_name  = Column(String(100))
    assist_name  = Column(String(100))
    event_type   = Column(String(20))   # Goal, Card, subst
    detail       = Column(String(50))   # Normal Goal, Yellow Card, etc.

    match = relationship("Match", back_populates="events")


# --- Table 4: Standings ---
class Standing(Base):
    __tablename__ = "standings"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id   = Column(Integer, ForeignKey("matches.fixture_id"), nullable=True)
    team_id      = Column(Integer, ForeignKey("teams.team_id"))
    group_name   = Column(String(10))
    rank         = Column(Integer)
    points       = Column(Integer)
    played       = Column(Integer)
    won          = Column(Integer)
    drawn        = Column(Integer)
    lost         = Column(Integer)
    goals_for    = Column(Integer)
    goals_against= Column(Integer)
    goal_diff    = Column(Integer)
    form         = Column(String(10))   # e.g. "WWDLW"

    match = relationship("Match", back_populates="standings")


# --- Table 5: Players ---
class Player(Base):
    __tablename__ = "players"

    player_id  = Column(Integer, primary_key=True)
    name       = Column(String(100))
    nationality= Column(String(100))
    position   = Column(String(20))    # Goalkeeper, Defender, etc.
    age        = Column(Integer)
    height     = Column(String(10))
    weight     = Column(String(10))
    photo_url  = Column(String(255))
    team_id    = Column(Integer, ForeignKey("teams.team_id"))

    team  = relationship("Team",        back_populates="players")
    stats = relationship("PlayerStat",  back_populates="player")


# --- Table 6: Player stats per match ---
class PlayerStat(Base):
    __tablename__ = "player_stats"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id     = Column(Integer, ForeignKey("matches.fixture_id"))
    player_id      = Column(Integer, ForeignKey("players.player_id"))
    rating         = Column(Float)
    minutes_played = Column(Integer)
    goals          = Column(Integer)
    assists        = Column(Integer)
    shots_total    = Column(Integer)
    shots_on       = Column(Integer)
    passes_total   = Column(Integer)
    passes_key     = Column(Integer)
    tackles        = Column(Integer)
    yellow_cards   = Column(Integer)
    red_cards      = Column(Integer)

    player = relationship("Player", back_populates="stats")


# --- Create all tables ---
def init_db():
    Base.metadata.create_all(engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    init_db()
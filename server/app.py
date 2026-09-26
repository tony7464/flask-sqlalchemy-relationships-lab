#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


def bio_text_for(speaker):
    """Return the speaker's bio, or a fallback when none is stored."""
    if speaker.bio is None:
        return "No bio available"
    return speaker.bio.bio_text


@app.route('/events')
def get_events():
    """List every event as id, name, and location."""
    events = Event.query.all()
    payload = [
        {
            "id": event.id,
            "name": event.name,
            "location": event.location,
        }
        for event in events
    ]
    return jsonify(payload), 200


@app.route('/events/<int:id>/sessions')
def get_event_sessions(id):
    """List sessions belonging to one event."""
    event = db.session.get(Event, id)
    if event is None:
        return jsonify({"error": "Event not found"}), 404

    payload = [
        {
            "id": session.id,
            "title": session.title,
            "start_time": session.start_time.isoformat() if session.start_time else None,
        }
        for session in event.sessions
    ]
    return jsonify(payload), 200


@app.route('/speakers')
def get_speakers():
    """List every speaker as id and name."""
    speakers = Speaker.query.all()
    payload = [
        {
            "id": speaker.id,
            "name": speaker.name,
        }
        for speaker in speakers
    ]
    return jsonify(payload), 200


@app.route('/speakers/<int:id>')
def get_speaker(id):
    """Return one speaker together with their bio text."""
    speaker = db.session.get(Speaker, id)
    if speaker is None:
        return jsonify({"error": "Speaker not found"}), 404

    payload = {
        "id": speaker.id,
        "name": speaker.name,
        "bio_text": bio_text_for(speaker),
    }
    return jsonify(payload), 200


@app.route('/sessions/<int:id>/speakers')
def get_session_speakers(id):
    """List speakers assigned to one session, including bio text."""
    session = db.session.get(Session, id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    payload = [
        {
            "id": speaker.id,
            "name": speaker.name,
            "bio_text": bio_text_for(speaker),
        }
        for speaker in session.speakers
    ]
    return jsonify(payload), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)

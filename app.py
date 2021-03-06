#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'Show'

  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),primary_key=True)
  start_time= db.Column(db.DateTime(),nullable=False,primary_key=True)
  def __repr__(self):
    return f'<Show venueId: {self.venue_id} , artistId: {self.artist_id}, date: {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean , nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref= "Venue")

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref= "Artist")

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  

  data=[]
  selected = db.session.query(Venue).distinct('city',).all()
  for select in selected:
    venues = Venue.query.filter(Venue.city == select.city)
    temp= []
    for venu in venues:
      upcomingCount = Show.query.filter(Show.venue_id == venu.id, Show.start_time > datetime.now()).count()
      temp.append(
      {
      "id": venu.id,
      "name": venu.name,
      "num_upcoming_shows": upcomingCount
      }
      )
    data.append(
      {
    "city": select.city,
    "state": select.state,
    "venues": temp
      }
    )
      

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venues = Venue.query.filter(Venue.name.ilike(f'%{request.form.get("search_term", "")}%')).all()
  venuesCount= Venue.query.filter(Venue.name.ilike(f'%{request.form.get("search_term", "")}%')).count()
  
  data = []

  for venu in venues:
    upcomingCount = Show.query.filter(Show.venue_id == venu.id, Show.start_time > datetime.now()).count()
    data.append(
      {
      "id": venu.id,
      "name": venu.name,
      "num_upcoming_shows": upcomingCount,
    }
    )
  response={
    "count": venuesCount,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venueTemp = Venue.query.get(venue_id)
  pastShowsquery= Show.query.filter(Show.venue_id == venueTemp.id, Show.start_time < datetime.now()).all()
  pastShowsCount = len(pastShowsquery)
  past_shows = []

  for past in pastShowsquery:
    past_shows.append({
      "artist_id": past.artist_id,
      "artist_name": Artist.query.get(past.artist_id).name,
      "artist_image_link": Artist.query.get(past.artist_id).image_link,
      "start_time": str(past.start_time)
    })

  upcomingShowsquery =Show.query.filter(Show.venue_id == venueTemp.id, Show.start_time > datetime.now()).all()
  upcoming_shows= []
  upcomingShowCount = len(upcomingShowsquery)

  for upcoming in upcomingShowsquery:
    upcoming_shows.append({
      "artist_id": upcoming.artist_id,
      "artist_name": Artist.query.get(upcoming.artist_id).name,
      "artist_image_link": Artist.query.get(upcoming.artist_id).image_link,
      "start_time": str(upcoming.start_time)
    })
 
  print(venueTemp.genres)

  data={
    "id": venueTemp.id,
    "name": venueTemp.name,
    "genres": venueTemp.genres.replace('{','').replace('}','').split(','),
    "address": venueTemp.address,
    "city": venueTemp.city,
    "state": venueTemp.state,
    "phone": venueTemp.phone,
    "website": venueTemp.website,
    "facebook_link": venueTemp.facebook_link,
    "seeking_talent": venueTemp.seeking_talent,
    "seeking_description": venueTemp.seeking_description,
    "image_link": venueTemp.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": upcomingShowCount,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    genresData = []
    genres = request.form.getlist('genres')
    for genre in genres:
      genresData.append(genre)

    venueTemp = Venue(name=request.form['name'],city=request.form['city'],state=request.form['state'],address=request.form['address'],phone= request.form['phone'],image_link=request.form['image_link'],website=request.form['website'],facebook_link=request.form['facebook_link'],genres=genresData, seeking_talent=request.form['seeking_talent']=='true',seeking_description=request.form['seeking_description'])
    db.session.add(venueTemp)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()  
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    error= True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    if error:
      flash('Venue ' + venue_id + ' couldn\'t be deleted')
    else:
      flash('Venue ' + venue_id + ' was successfully deleted!')
    db.session.close()  
    return ''


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data=[]
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artists = Artist.query.filter(Artist.name.ilike(f'%{request.form.get("search_term", "")}%')).all()
  artistCount = len(artists)

  data= []
  for artist in artists:
    upcomingCount = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcomingCount,
    })

  response={
    "count": artistCount,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  pastShowsquery= Show.query.filter(Show.artist_id == artist.id, Show.start_time < datetime.now()).all()
  pastShowsCount = len(pastShowsquery)
  past_shows = []

  for past in pastShowsquery:
    past_shows.append({
      "venue_id": past.venue_id,
      "venue_name": Venue.query.get(past.venue_id).name,
      "venue_image_link": Venue.query.get(past.venue_id).image_link,
      "start_time": str(past.start_time)
    })

  upcomingShowsquery =Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).all()
  upcoming_shows= []
  upcomingShowCount = len(upcomingShowsquery)

  for show in upcomingShowsquery:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "venue_image_link": Venue.query.get(show.venue_id).image_link,
      "start_time": str(show.start_time)
    })
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.replace('{','').replace('}','').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": upcomingShowCount,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artistTemp = Artist.query.get(artist_id)
  artist={
    "id": artistTemp.id,
    "name": artistTemp.name,
    "genres": artistTemp.genres.replace('{','').replace('}','').split(','),
    "city": artistTemp.city,
    "state": artistTemp.state,
    "phone": artistTemp.phone,
    "website": artistTemp.website,
    "facebook_link": artistTemp.facebook_link,
    "seeking_venue": artistTemp.seeking_venue,
    "seeking_description": artistTemp.seeking_description,
    "image_link": artistTemp.image_link

  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    genresData = []
    genres = request.form.getlist('genres')
    for genre in genres:
      genresData.append(genre)
    artistTemp = Artist.query.get(artist_id)
    artistTemp.name= request.form['name']
    artistTemp.city= request.form['city']
    artistTemp.state= request.form['state']
    artistTemp.phone= request.form['phone']
    artistTemp.genres= genresData
    artistTemp.image_link= request.form['image_link']
    artistTemp.facebook_link= request.form['facebook_link']
    artistTemp.website =  request.form['website']
    artistTemp.seeking_venue= request.form['seeking_venue'] == 'true'
    artistTemp.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()  
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueTemp = Venue.query.get(venue_id)
  
  venue={
    "id": venue_id,
    "name": venueTemp.name,
    "genres": venueTemp.genres.replace('{','').replace('}','').split(','),
    "address": venueTemp.address,
    "city": venueTemp.city,
    "state": venueTemp.state,
    "phone": venueTemp.phone,
    "website": venueTemp.website,
    "facebook_link": venueTemp.facebook_link,
    "seeking_talent": venueTemp.seeking_talent,
    "seeking_description": venueTemp.seeking_description,
    "image_link": venueTemp.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    genresData = []
    genres = request.form.getlist('genres')
    for genre in genres:
      genresData.append(genre)
    venueTemp = Venue.query.get(venue_id)
    venueTemp.name= request.form['name']
    venueTemp.city= request.form['city']
    venueTemp.state= request.form['state']
    venueTemp.address= request.form['address']
    venueTemp.phone= request.form['phone']
    venueTemp.genres= genresData
    venueTemp.facebook_link= request.form['facebook_link']
    venueTemp.image_link= request.form['image_link']
    venueTemp.website= request.form['website']
    venueTemp.seeking_talent=request.form['seeking_talent']=='true'
    venueTemp.seeking_description=request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()  
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    genresData = []
    genres = request.form.getlist('genres')
    for genre in genres:
      genresData.append(genre)

    artistTemp = Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],phone= request.form['phone'],genres=genresData,image_link=request.form['image_link'],facebook_link=request.form['facebook_link'],website=request.form['website'], seeking_venue=request.form['seeking_venue']=='true',seeking_description=request.form['seeking_description'])
    db.session.add(artistTemp)
    db.session.commit()
  except:
    error = True
    db.session.rollback()  
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  showsTemp = Show.query.all()
  data=[]
  for show in showsTemp:
    data.append(
      {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    showTemp = Show(venue_id=request.form['venue_id'],artist_id=request.form['artist_id'],start_time=request.form['start_time'])

    print(showTemp)

    db.session.add(showTemp)
    db.session.commit()
  except:
    error = True
    db.session.rollback()  
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

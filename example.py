from src.spreddit import Spreddit

# initialize Spreddit
spr = Spreddit()

# Initialize Reddit Account with API. This contains a login.
# All mentioned params in brackets have to be filled.
spr.initRedditAccount(user = '',
                      pw = '',
                      app_id = '',
                      secret = '',
                      os = 'Windows',
                      app_name = '',
                      app_vers = '')

# Initialize instagram account. This contains a login.
spr.initInstagramAccount(user = '',
                         pw = '')

# Define a bunch of hashtags and set them.
lsIgHashtags = ['love', 'photooftheday', 'travel', \
                'photography', 'hiking', 'beautiful', \
                'picoftheday', 'naturephotography', 'landscape', \
                'photo', 'travelphotography', 'adventure', \
                'naturelovers', 'life', 'explore', \
                'wildlife', 'beautifuldestinations', 'nature_perfection', \
                'naturephotography', 'wanderlust']

spr.instagram.setHashtags(lsIgHashtags)

# Initialize picture folder and storage dump on disk
spr.initStorage()

# check a chosen subreddit and save pictures from it
spr.saveNewPostsFromReddit(subReddit = '')

# This is where the magic happens - SPREAD IT!
spr.spreadPost(spr.SMT_INSTAGRAM)


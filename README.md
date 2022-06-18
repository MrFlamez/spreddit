# spreddit

### Description

A tool which can spread posts from reddit to other social media platforms. The one and only supported platform until now is instagram. Further platforms are planned.

#### Details

- All new pictures from a selected subreddit since last run will be saved on disk. The time of last run will be set during initialization at current time. So it is possible to track posts of a subreddit and save them. For this, its neccessary to call the script periodically.

- The collected images will be saved in subfolder "pictures" on disk in the same folder as the script is running. Additionally a file with ja minimalistic database will stored on disk. It's a pickle dump from Storage object.

- A post on other social media platforms always contains the content of original reddit post with credits. After that, the hashtags will append.

- After successfull posting, the picture will deleted to avoid double-post.

#### Features

- [x] save Image-Posts from Subreddit
- [x] publishing on Instagram
- [ ] publishing on Tumblr
- [ ] delayed actions on instagram to avoid spam detection
- [ ] make save location on disk selectable

---

### Prerequisites

- python 3

- python modules named in requirements.txt
  
  ```pip -r requirements.txt```

- Reddit account with API access

  (Guide: https://towardsdatascience.com/how-to-use-the-reddit-api-in-python-5e05ddfd1e5c)

- social media accounts of at least one of the following platforms
  - Instagram

---

### Example

An example can be find at example.py. It contains a step-by-step guide with comments.
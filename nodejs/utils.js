const tweetExample = {
  _type: "snscrape.modules.twitter.Tweet",
  url: "https://twitter.com/maliksblr92/status/1638192730021961731",
  date: "2023-03-21T14:55:57+00:00",
  rawContent: "love2222",
  renderedContent: "love2222",
  id: 1638192730021961700,
  user: {
    _type: "snscrape.modules.twitter.User",
    username: "maliksblr92",
    id: 871226174550286300,
    displayname: "programmer",
    rawDescription:
      "Multi Full Stack Developer \n" +
      "Consultant at Systems Limited \n" +
      "Find me here...\n" +
      "https://t.co/SEI3pQKWLA\n" +
      "https://t.co/GTPbQVBY41…",
    renderedDescription:
      "Multi Full Stack Developer \n" +
      "Consultant at Systems Limited \n" +
      "Find me here...\n" +
      "github.com/ratroot92\n" +
      "linkedin.com/in/ahmed-kabee…",
    descriptionLinks: [[Object], [Object]],
    verified: false,
    created: "2017-06-04T04:44:41+00:00",
    followersCount: 19,
    friendsCount: 94,
    statusesCount: 464,
    favouritesCount: 61,
    listedCount: 0,
    mediaCount: 82,
    location: "Islamabad, Pakistan",
    protected: false,
    link: {
      _type: "snscrape.modules.twitter.TextLink",
      text: "github.com/ratroot92",
      url: "https://github.com/ratroot92",
      tcourl: "https://t.co/L0DkiYS3Ic",
      indices: [Array],
    },
    profileImageUrl:
      "https://pbs.twimg.com/profile_images/878355534310760448/ujZlrhk-_normal.jpg",
    profileBannerUrl:
      "https://pbs.twimg.com/profile_banners/871226174550286336/1496587433",
    label: null,
    description:
      "Multi Full Stack Developer \n" +
      "Consultant at Systems Limited \n" +
      "Find me here...\n" +
      "github.com/ratroot92\n" +
      "linkedin.com/in/ahmed-kabee…",
    descriptionUrls: [[Object], [Object]],
    linkTcourl: "https://t.co/L0DkiYS3Ic",
    linkUrl: "https://github.com/ratroot92",
    url: "https://twitter.com/maliksblr92",
  },
  replyCount: 0,
  retweetCount: 0,
  likeCount: 0,
  quoteCount: 0,
  conversationId: 1638192730021961700,
  lang: "en",
  source:
    '<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>',
  sourceUrl: "https://mobile.twitter.com",
  sourceLabel: "Twitter Web App",
  links: null,
  media: null,
  retweetedTweet: null,
  quotedTweet: null,
  inReplyToTweetId: null,
  inReplyToUser: null,
  mentionedUsers: null,
  coordinates: null,
  place: null,
  hashtags: null,
  cashtags: null,
  card: null,
  viewCount: null,
  vibe: null,
  content: "love2222",
  outlinks: [],
  outlinksss: "",
  tcooutlinks: [],
  tcooutlinksss: "",
  username: "maliksblr92",
};

const jsUtils = {
  parseBody: function (tweet) {
    console.log("======================================");
    console.log(JSON.parse(tweet));
    console.log("======================================");

    return tweet;
  },
};
module.exports = jsUtils;

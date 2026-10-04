# -----------------------------------
# Brand Configuration
# -----------------------------------
#
# Sentiment vocabulary (version 2). Words and phrases are written in the
# form the cleaning step produces: lowercase, apostrophes removed
# ("can't" -> "cant"). Each entry has a weight:
#     words:   +/-1 normal, +/-2 strong (listed separately)
#     phrases: +/-2 (a phrase is a clearer signal than a single word)
# The vocabulary was chosen from general knowledge of payment-app
# complaints and praise plus the DEVELOPMENT half of the reviews only;
# the TEST half is used to check the result (see sentiment/validate.py).

from brands import get_brand, DEFAULT_BRAND

# The vocabulary below is shared by every brand. brand_name, industry,
# play_store and brand_keywords are the DEFAULT brand's; the dashboard and
# pipeline pass the selected brand explicitly (see brands.py).
_default = get_brand(DEFAULT_BRAND)

brand_config = {
    "brand_name": _default["name"],

    "industry": _default["industry"],

    # Google Play source settings (the brand's app)
    "play_store": {
        "app_id": _default["app_id"],
        "country": _default["country"],
        "lang": _default["lang"],
        "review_count": _default["review_count"],
    },

    # Sources where every item is about the brand itself, so the keyword
    # check is not required (reviews on the brand's own store page)
    "brand_specific_sources": ["Google Play"],

    # Terms used to identify mentions related to the brand
    "brand_keywords": _default["keywords"],

    # ---------------- Positive vocabulary ----------------
    "positive_words": [
        "good", "great", "nice", "fast", "quick", "speedy", "instant",
        "instantly", "reliable", "stable", "smooth", "easy", "simple",
        "helpful", "happy", "satisfied", "pleased", "pleasant", "cool",
        "fine", "secure", "safe", "trusted", "trust", "convenient",
        "seamless", "efficient", "responsive", "affordable", "clear",
        "strong", "solid", "legit", "genuine", "friendly", "userfriendly",
        "thanks", "thank", "recommend", "recommended", "kudos", "congrats",
        "congratulations", "impressive", "impressed", "enjoy", "enjoying",
        "enjoyed", "appreciate", "appreciated", "worth", "wow", "sweet",
        "valid", "hasslefree", "magnificent",
        # food, travel and delivery
        "delicious", "tasty", "yummy", "fresh", "comfortable", "courteous",
        "punctual", "polite", "cheap", "cheaper", "tidy", "crispy"
    ],

    "strong_positive_words": [
        "excellent", "amazing", "awesome", "fantastic", "exceptional",
        "perfect", "outstanding", "superb", "brilliant", "wonderful",
        "flawless", "best", "love", "loved", "topnotch", "incredible"
    ],

    "positive_phrases": [
        "no problem", "no wahala", "no stress", "well done", "thank you",
        "keep it up", "keep it on", "keep up", "top notch", "easy to use",
        "user friendly", "works well", "work well", "working well",
        "works perfectly", "highly recommend", "god bless", "good job",
        "great job", "i like", "i really like", "like this app",
        "does the job", "hassle free", "100 percent"
    ],

    # ---------------- Negative vocabulary ----------------
    "negative_words": [
        "slow", "bad", "poor", "weak", "fail", "failed", "fails", "failure",
        "failing", "stuck", "pending", "delay", "delayed", "delays",
        "glitch", "glitches", "bug", "bugs", "buggy", "crash", "crashes",
        "crashed", "crashing", "freeze", "freezes", "frozen", "freezing",
        "blocked", "restricted", "restriction", "suspended", "deducted",
        "overcharged", "expensive", "overpriced", "unreliable", "unstable",
        "disappointed", "disappointing", "disappointment", "frustrating",
        "frustrated", "frustration", "annoying", "annoyed", "angry",
        "upset", "sad", "problem", "problems", "issue", "issues", "error",
        "errors", "wahala", "stress", "stressful", "stressing", "complain",
        "complaint", "complaints", "unable", "lost", "missing", "difficult",
        "unavailable", "rejected", "declined", "harassment", "harass",
        "harassing", "forcefully", "forced", "spam", "excessive", "lag",
        "laggy", "hate", "hated", "regret", "disconnected", "wrong", "rude",
        "ignore", "ignored", "ignoring", "unprofessional", "cancelled",
        "cancelling", "canceled", "canceling", "unserious", "inconvenient",
        "compromised", "hacked", "unsafe", "insecure", "complicated",
        "confusing", "tedious",
        # food, travel and delivery
        "stale", "cold", "late", "dirty", "overcrowded", "expired", "burnt",
        "undercooked", "tasteless", "overbooked", "rescheduled"
    ],

    "strong_negative_words": [
        "terrible", "horrible", "awful", "worst", "scam", "scammer",
        "scammers", "scammed", "fraud", "fraudulent", "thief", "thieves",
        "stole", "stolen", "steal", "fake", "rubbish", "nonsense", "trash",
        "garbage", "sucks", "wicked", "cheat", "cheated", "cheaters",
        "ridiculous", "disgusting", "pathetic", "nightmare", "worthless",
        "lied", "liar", "liars", "useless"
    ],

    "negative_phrases": [
        "not working", "dont work", "doesnt work", "did not work",
        "stopped working", "stop working", "keeps crashing",
        "not responding", "no response", "no reply", "not available",
        "not able", "unable to", "cant login", "cant log in", "cant open",
        "cant download", "cant install", "cant transfer", "cant access",
        "cant use", "wont open", "wont load", "wont work", "wont let me",
        "not getting", "not received", "didnt receive", "not credited",
        "not reflecting", "not loading", "debited but", "money stuck",
        "waste of time", "waste of data", "too high", "too much",
        "too slow", "no network", "dont like", "do not like", "didnt like",
        "no help", "worst app", "fix this", "fix your", "fix ur",
        "please fix", "keeps asking", "keeps saying", "keeps cancelling",
        "keep cancelling", "take days", "takes days", "takes long",
        "take long", "take forever", "takes forever", "to no avail",
        "not allowed", "not allow", "will not allow", "wont allow",
        "holding my money", "no longer", "not showing", "not saved",
        "hard to", "not ok", "not okay"
    ],

    # Words that flip the meaning of a sentiment word shortly after them
    "negation_words": [
        "not", "no", "never", "neither", "nor", "hardly", "dont", "doesnt",
        "didnt", "isnt", "wasnt", "arent", "cant", "cannot", "wont",
        "couldnt", "wouldnt", "shouldnt", "without", "nothing", "aint"
    ],

    # Words that double the strength of the sentiment word after them
    "intensifiers": [
        "very", "extremely", "really", "highly", "absolutely", "incredibly",
        "so", "too", "super", "totally", "truly", "completely", "damn"
    ]
}

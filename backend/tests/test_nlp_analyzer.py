import pytest

from app.services.nlp_analyzer import analyse_text, compute_quick_score


class TestAnalyseText:
    def test_basic_text_returns_nlp_features(self):
        text = "This is a shocking revelation that will change everything you know about AI!"
        features = analyse_text(text, "twitter")
        assert features.word_count == 13
        assert features.char_count == len(text)
        assert features.sentence_count >= 1
        assert 0 <= features.flesch_reading_ease <= 100
        assert features.vader_compound != 0.0
        assert features.has_curiosity_gap is True
        assert features.power_word_count >= 1
        assert "shocking" in features.power_words_found

    def test_question_detection(self):
        text = "Did you know this? What about that? Here are the facts."
        features = analyse_text(text, "general")
        assert features.has_questions is True
        assert features.question_count == 2

    def test_hashtag_extraction(self):
        text = "Great tips for #marketing and #growth today"
        features = analyse_text(text, "twitter")
        assert features.hashtag_count == 2
        assert "#marketing" in features.hashtags
        assert "#growth" in features.hashtags

    def test_emoji_detection(self):
        text = "This is amazing! 🔥🚀 Check it out"
        features = analyse_text(text, "instagram")
        assert features.emoji_count == 2

    def test_platform_fit_twitter_optimal(self):
        text = "Short punchy tweet #viral"
        features = analyse_text(text, "twitter")
        assert 0 <= features.length_fit_score <= 100
        assert 0 <= features.hashtag_fit_score <= 100

    def test_platform_fit_linkedin_long(self):
        text = "A " * 700  # ~1400 chars, within LinkedIn optimal
        features = analyse_text(text, "linkedin")
        assert features.length_fit_score > 50

    def test_cta_detection(self):
        text = "Follow me for more tips and share this with your friends!"
        features = analyse_text(text, "instagram")
        assert features.has_cta is True

    def test_controversy_markers(self):
        text = "Unpopular opinion: this is the worst take I've seen"
        features = analyse_text(text, "twitter")
        assert features.has_controversy is True

    def test_personal_story_markers(self):
        text = "I learned something incredible from my experience last year"
        features = analyse_text(text, "linkedin")
        assert features.has_personal_story is True

    def test_urgency_markers(self):
        text = "Breaking news just happened now! Limited time offer"
        features = analyse_text(text, "twitter")
        assert features.has_urgency is True

    def test_list_format_detection(self):
        text = "1. First thing\n2. Second thing\n3. Third thing"
        features = analyse_text(text, "linkedin")
        assert features.has_list_format is True

    def test_first_line_extraction(self):
        text = "This is the hook line.\nThis is the body."
        features = analyse_text(text, "twitter")
        assert features.first_line == "This is the hook line."


class TestQuickScore:
    def test_quick_score_range(self):
        text = "Check out this amazing hack for productivity! #tips"
        features = analyse_text(text, "twitter")
        score = compute_quick_score(features)
        assert 0 <= score <= 100

    def test_high_engagement_text_scores_higher(self):
        boring = "The meeting is at 3pm."
        engaging = "🔥 Shocking secret hack that will BLOW YOUR MIND! Share this now! #viral #trending"
        boring_score = compute_quick_score(analyse_text(boring, "twitter"))
        engaging_score = compute_quick_score(analyse_text(engaging, "twitter"))
        assert engaging_score > boring_score

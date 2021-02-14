#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tgcat.h"
#include "utils.h"

#include "category_detect.h"
#include "lang_detect.h"

#include "fasttext/fasttext.h"

using namespace std;

map<string, double> settings;
vector<string> categories;

fasttext::FastText langFastText;
fasttext::FastText ruCatFastText;
fasttext::FastText enCatFastText;

int tgcat_init()
{
    settings = load_settings("resources/settings.txt");
    categories = get_category_list("resources/categories.list");

	langFastText.loadModel("resources/lid.176.bin");
	ruCatFastText.loadModel("resources/ru_cat_rusvectores_1.0lr_5n.ftz");
	enCatFastText.loadModel("resources/en_cat_model_0.1lr.100.ftz");
    return 0;
}

int tgcat_detect_language(const struct TelegramChannelInfo *channel_info, char language_code[6])
{
	setlocale(LC_ALL, "");

	TelegramChannel telegramChannel(channel_info->title, channel_info->description, channel_info->post_count, channel_info->posts);
	wstring text = telegramChannel.get_all_text();
	pair<string, double> lang_score = detect_language(langFastText, settings, text);
    memcpy(language_code, lang_score.first.c_str(), lang_score.first.size() + 1);
    return 0;
}

int tgcat_detect_category(const struct TelegramChannelInfo *channel_info, double category_probability[TGCAT_CATEGORY_OTHER + 1])
{
    TelegramChannel telegramChannel(channel_info->title, channel_info->description, channel_info->post_count, channel_info->posts);
    wstring text = telegramChannel.get_all_text();
    pair<string, double> lang_score = detect_language(langFastText, settings, text);
    vector<double> probabilities;

    if(lang_score.first == "ru")
    {
        wstring ru_text = transform_by_regex(text, wregex(L"[^a-zа-я ]"));
        probabilities = get_category_probabilities(ruCatFastText, categories, ru_text);
    }
    else if(lang_score.first == "en")
    {
        wstring en_text = transform_by_regex(text, wregex(L"[^a-z ]"));
        probabilities = get_category_probabilities(enCatFastText, categories, en_text);
    }

    memset(category_probability, 0, sizeof(double) * (TGCAT_CATEGORY_OTHER + 1));

    for (int i = 0, len = probabilities.size(); i < len; i++)
    {
        category_probability[i] = probabilities[i];
    }

    return 0;
}

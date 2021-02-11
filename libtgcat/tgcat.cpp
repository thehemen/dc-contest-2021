#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tgcat.h"
#include "utils.h"
#include "lang_detect.h"

#include "fasttext/fasttext.h"

using namespace std;

fasttext::FastText fastText;
map<string, double> settings;

int tgcat_init()
{
    settings = load_settings("../resources/settings.txt");
	fastText.loadModel("../resources/lid.176.bin");
    return 0;
}

int tgcat_detect_language(const struct TelegramChannelInfo *channel_info, char language_code[6])
{
	setlocale(LC_ALL, "");

	TelegramChannel telegramChannel(channel_info->title, channel_info->description, channel_info->post_count, channel_info->posts);
	wstring text = telegramChannel.get_all_text();
	pair<string, double> lang_score = detect_language(fastText, settings, text);
    memcpy(language_code, lang_score.first.c_str(), lang_score.first.size() + 1);
    return 0;
}

int tgcat_detect_category(const struct TelegramChannelInfo *channel_info, double category_probability[TGCAT_CATEGORY_OTHER + 1])
{
    (void)channel_info;
    memset(category_probability, 0, sizeof(double) * (TGCAT_CATEGORY_OTHER + 1));
    int i;

    for (i = 0; i < 10; i++)
    {
        category_probability[rand() % (TGCAT_CATEGORY_OTHER + 1)] += 0.1;
    }

    return 0;
}

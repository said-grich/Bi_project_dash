from googletrans import  Translator
from deep_translator import GoogleTranslator

if __name__=='__main__':

    translated = GoogleTranslator(source='auto', target='en').translate(
        "انا اهواك")
    print(translated)
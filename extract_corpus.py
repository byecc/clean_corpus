import re
from langconv import *
class Paragraph(object):
    def __init__(self):
        self.sentences = []
        self.sentiment = None

class Mark:
    def __init__(self):
        self.word_now = []
        self.word_origin = []
        self.label = []
        self.emo = []

class Process:
    def clean_str(self,string):
        string = Converter('zh-hans').convert(string)
        string = self.DBC2SBC(string)
        string = re.sub(r"&ldquo;?", "“", string)
        string = re.sub(r"&rsquo;?", "’", string)
        string = re.sub(r"&lsquo;?", "‘", string)
        string = re.sub(r"&nbsp;?", " ", string)
        string = re.sub(r"&rarr;?", "", string)
        string = re.sub(r"◆", " ", string)
        string = re.sub(r"■", " ", string)
        string = re.sub(r"●", " ", string)
        string = re.sub(r"▼", " ", string)
        string = re.sub(r"⊙", " ", string)
        string = re.sub(r"○", " ", string)
        string = re.sub(r"◎", " ", string)
        string = re.sub(r"\s+", "", string)
        return string.strip()

    @staticmethod
    def DBC2SBC(string):
        rstring = ""
        for uchar in string:
            inside_code = ord(uchar)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
            if inside_code < 0x0020 or inside_code > 0x7e:
                rstring += uchar
            else:
                rstring += chr(inside_code)
        return rstring


    def new_read_file(self,path,outpath1 = "./outpath1",outpath2 = "./outpath2"):
        with open(path,'r',encoding='utf8') as fin,open(outpath1,'w',encoding='utf8') as esout,open(outpath2,'w',encoding='utf8') as psout:
            p = Paragraph()
            para_count = 0
            for idx,line in enumerate(fin):
                line = self.clean_str(line)
                # print(idx)
                if line.startswith('<'):
                    p.sentiment = line[1:len(line)-1]
                elif line == "":
                    assert p.sentiment is not None
                    # psout.write(str(para_count)+'\t'+str(len(p.sentences))+'\t'+p.sentiment+'\n')
                    # print(str(para_count)+'\t'+str(len(p.sentences))+'\t'+p.sentiment+'\n')
                    para_count +=1
                    p = Paragraph()
                else:
                    sentence = self.mark_sentence_entity(line)
                    sentence = self.finish_sentence(sentence)
                    p.sentences.append(sentence)
                    # print(sentence)
                    mark = self.new_extract_mark(sentence)
                    word_len = len(mark.word_now)
                    for i in range(word_len):
                        esout.write(mark.word_now[i] + '\t' + mark.word_origin[i] + '\t' + mark.label[i] + '\t' + mark.emo[i] + '\n')
                    esout.write('\n')

    @staticmethod
    def new_sub_single(matched):
        return " "+matched.group("single")+"|||"+matched.group("single")+" "
    @staticmethod
    def new_sub_num(matched):
        return " "+matched.group("number")+"|||" + matched.group("number") + " "
    @staticmethod
    def new_sub_letters(matched):
        return " "+matched.group("letters")+"|||" + matched.group("letters") + " "
    @staticmethod
    def new_mixed(matched):
        return " "+matched.group("mixed")+"|||" + matched.group("mixed") + " "
    @staticmethod
    def new_sub_entity(matched):
        return "`"+matched.group("entity")+"`"

    def mark_sentence_entity(self,sentence):
        # sentence = re.sub("(?P<single>[0-9a-zA-Z\.]{2,})", self.new_sub_single, sentence)
        # sentence = re.sub("(?P<number>[0-9\.]{2,})", self.new_sub_num, sentence)
        sentence = re.sub("(?P<entity>(\[\[(.*?)\]\]\s{0,1}<\S{1,2}>))",self.new_sub_entity,sentence)
        return sentence

    def finish_sentence(self,text):
        pos = 0
        entity_list = []
        other_list = []
        finish_sentence = ""
        while pos < len(text):
            ch = text[pos]
            if ch == '`':
                if len(other_list) >0 :
                    other = ''.join(other_list)
                    # other = re.sub("(?P<letters>[a-zA-Z]{2,})", self.new_sub_letters, other)
                    # finish_sentence += re.sub("(?P<number>([0-9]+\.{0,1}){0,1}[0-9]+)", self.new_sub_num, other)
                    finish_sentence += re.sub("(?P<mixed>([0-9]+[\.,:-]{0,1})*[0-9]+|[0-9a-zA-Z+]{2,})", self.new_mixed, other)
                    other_list = []
                pos += 1
                ch = text[pos]
                while ch !='`':
                    entity_list.append(ch)
                    pos+=1
                    ch = text[pos]
                entity = ''.join(entity_list).replace(' ','')
                finish_sentence +=re.sub("(?P<single>[0-9a-zA-Z\.]{2,})",self.new_sub_single,'`'+entity+'`')
                entity_list = []
                pos += 1
            else:
                other_list.append(ch)
                pos+=1
        if len(other_list) > 0:
            other = ''.join(other_list)
            # other = re.sub("(?P<letters>[a-zA-Z]{2,})", self.new_sub_letters, other)
            # finish_sentence += re.sub("(?P<number>([0-9]+\.{0,1}){0,1}[0-9]+)", self.new_sub_num, other)
            finish_sentence += re.sub("(?P<mixed>([0-9]+[\.,:-]{0,1})*[0-9]+|[0-9a-zA-Z+]{2,})", self.new_mixed, other)
        return finish_sentence

    def new_extract_mark(self,text):
        mark = Mark()
        pos = 0
        sub_list = []
        entity_list = re.findall(r"\[\[(.*?)\]\]", text)
        entity_count = 0
        while pos < len(text):
            ch = text[pos]
            if ch == ' ':
                pos += 1
                ch = text[pos]
                while ch != ' ':
                    sub_list.append(ch)
                    pos += 1
                    ch = text[pos]
                sub = ''.join(sub_list)
                assert len(sub.split('|||')) == 2
                sub = sub.strip()
                mark.word_now.append(sub.split('|||')[0])
                mark.word_origin.append(sub.split('|||')[1])
                mark.label.append('o')
                mark.emo.append('o')
                sub_list = []
                pos += 1
            elif ch=='`':
                pos += 1
                ch = text[pos]
                while ch!='`':
                    sub_list.append(ch)
                    pos += 1
                    ch = text[pos]
                sub = ''.join(sub_list)
                subsp = sub[2:len(sub)-1].split(']]<')
                assert len(subsp) == 2
                now,origin,label,emo = self.extract_entity(subsp[0],subsp[1])
                mark.word_now.extend(now)
                mark.word_origin.extend(origin)
                mark.label.extend(label)
                mark.emo.extend(emo)
                sub_list = []
                pos += 1
                entity_count += 1
            else:
                mark.word_now.append(ch)
                mark.word_origin.append(ch)
                mark.label.append('o')
                mark.emo.append('o')
                pos += 1
        assert entity_count == len(entity_list)
        return mark

    def extract_entity(self,text,sentiment):
        pos = 0
        sub_list = []
        now,origin,label,emo = [],[],[],[]
        index = 0
        while pos<len(text):
            ch = text[pos]
            if ch == ' ':
                pos+=1
                ch = text[pos]
                while ch!=' ':
                    sub_list.append(ch)
                    pos+=1
                    ch = text[pos]
                sub = ''.join(sub_list)
                sub_list = []
                singles = sub.split('|||')
                now.append(singles[0])
                origin.append(singles[0])
                emo.append(sentiment)
                if index == 0:
                    if pos == len(text)-1:
                        label.append('s')
                        break
                    else:
                        label.append('b')
                        index+=1
                else:
                    label.append('m')
                pos+=1
            else:
                now.append(ch)
                origin.append(ch)
                emo.append(sentiment)
                pos+=1
                if index == 0:
                    if pos == len(text):
                        label.append('s')
                        break
                    else:
                        label.append('b')
                        index += 1
                else:
                    label.append('m')
        if len(label)>=2:
            label[len(label)-1] = 'e'
        return now,origin,label,emo

def verify(path):
    with open(path,'r',encoding='utf8') as fin:
        sign = 0
        for idx,line in enumerate(fin):
            if line!='\n':
                label = line.split('\t')[2]
                if label == 'b':
                    if sign == 0:
                        sign = 1
                    else:
                        print(idx,'b error')
                elif label == 'm':
                    if sign == 1:
                        sign = 1
                    else:
                        print(idx,'m error')
                elif label == 'e':
                    if sign == 1 or sign == 2:
                        sign = 0
                    else:
                        print(idx,'e error')
                elif label == 'o':
                    if sign != 0:
                        print(idx,'o error')


if __name__ == "__main__":
    Process().new_read_file("zhaohang_data/test.txt")
    verify('./outpath1')
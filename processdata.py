import random
import re
import os
from langconv import *
import time

random.seed(5)

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return len(self.items)==0

    def push(self,item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        if not self.isEmpty():
            return self.items[len(self.items)-1]
        else:
            # print('stack is empty')
            return -1

    def size(self):
        return len(self.items)

    def clean(self):
        self.items = []

class Paragraph:
    def __init__(self):
        self.sentences = []

    def show(self):
        for s in self.sentences:
            print(s)

class Process:
    def __init__(self):
        self.result=[]

    def read_file(self,corpus_file):
        with open(corpus_file,'r',encoding='utf8') as f:
            text = f.read()
            for t in text.split('\n\n'):
                self.result.append(self.clean_str(t))
                # print(self.clean_str(t))

    def write_clean_file(self):
        with open('data/clean_wind_1000_01.dat','a',encoding='utf8') as f:
            for r in self.result:
                f.write(r+'\n\n')


    def get_paragraphs(self,parameter):
        if os.path.exists(parameter.split_corpus_file):
            print('exists')
            return None
        with open(parameter.split_corpus_file,'a',encoding='utf8') as file:
            random_list = []
            random_index = random.randrange(0,len(self.result)-1)
            while len(random_list) < parameter.extract_num:
                if random_index in random_list:
                    random_index = random.randrange(0,len(self.result)-1)
                else:
                    random_list.append(random_index)
            assert len(random_list)==len(set(random_list))
            for r in random_list:
                print(r,'--------')
                file.write(self.result[r]+'\n\n')
    '''
        繁体->简体
        全角->半角 
        多个空格->一个空格
        html占位符替换
        特殊符号删除
    '''
    def clean_str(self,string):
        string = Converter('zh-hans').convert(string)
        string = self.DBC2SBC(string)
        string = re.sub(r"\s+"," ",string)
        string = re.sub(r"&ldquo;","“",string)
        string = re.sub(r"&rsquo;","’",string)
        string = re.sub(r"&lsquo;","‘",string)
        string = re.sub(r"&nbsp;"," ",string)
        string = re.sub(r"&rarr;","",string)
        string = re.sub(r"◆"," ",string)
        string = re.sub(r"■"," ",string)
        string = re.sub(r"●"," ",string)
        string = re.sub(r"▼"," ",string)
        string = re.sub(r"⊙"," ",string)
        string = re.sub(r"○"," ",string)
        string = re.sub(r"◎"," ",string)
        # print(string)
        return string

    def DBC2SBC(self,string):  #全半角转换
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

    def sentences_tokenize(self):
        paragraph_list = []
        cut_list = ["。"," ","”","！","？","!","?"]
        l_pair = ['(','（','{','《','[','【']
        r_pair = [')','）','}','》',']','】']
        ellip =  []
        punc_stack = Stack()
        starttime = time.time()
        for r in self.result:
            sentence = []
            p = Paragraph()
            for i,ch in enumerate(r):
                sentence.append(ch)
                if ch in l_pair:    #匹配左右对称的标点
                    punc_stack.push(ch)
                    continue
                if ch in r_pair:
                    if not punc_stack.isEmpty() :
                        if l_pair.index(punc_stack.peek())==r_pair.index(ch):
                            punc_stack.pop()
                    continue
                if punc_stack.isEmpty():  # 栈空，保证左右标点都匹配完了
                    if ch == '”':  #只有”需要考虑前一位和后一位的情况，其他普遍情况只需考虑后一位
                        if r[i-1] in cut_list and i!=len(r)-1 and r[i+1] not in cut_list:
                            sentence = ''.join(sentence)
                            p.sentences.append(sentence)
                            sentence = []
                    elif ch=='.':
                        if i<len(r)-1 and not str(r[i+1]).isdigit():
                            ellip.append(ch)
                        if i<len(r)-1 and r[i+1]!='.'and len(ellip) >= 2 and r[i+1] not in cut_list:
                            sentence = ''.join(sentence)
                            p.sentences.append(sentence)
                            sentence = []
                            ellip = []
                    else:
                        if ch in cut_list and i<len(r)-1 and r[i+1] not in cut_list and r[i+1]!='.': #正常list append终止条件，该字符在cut_list，且下一个不在cut_list。考虑一下边界条件
                            sentence = ''.join(sentence)
                            p.sentences.append(sentence)
                            sentence = []
            if len(sentence)>0:     #段落结束无终止符，且句子长度大于0
                sentence = ''.join(sentence)
                p.sentences.append(sentence)
            punc_stack.clean()     #段落结束清空栈，防止句子中缺失pair
            paragraph_list.append(p)
        print("time:",time.time()-starttime)
        return paragraph_list

    '''
    句子长度统计：
        统计所有段落的所有句子数量
        统计大于threshold的句子数量
            '''
    def statistic(self,paragraph_list,threshold):
        s_list=[]
        all_sen = 0
        for i,p in enumerate(paragraph_list):
            print('第',i+1,'段：')
            for j,s in enumerate(p.sentences):
                all_sen+=1
                # print(j+1,'句len：',len(s),end='')
                if len(s) > threshold:
                    s_list.append(str(i)+' '+str(j))
            print()
        print('所有句子数量：',all_sen)
        print('句子长度大于',threshold,'的句子数量：',len(s_list))
        for s in s_list:
            print(s)
            ss = s.split(' ')
            print(paragraph_list[int(ss[0])].sentences[int(ss[1])])

# p = Process()
# print(p.clean_srt("www.stcn.com/123.pfd）04,月           12日讯（601601）32.41%4月12日343.456晚說明檔案www.123.se.co，http://12.sd.we公司董事长高国富因工作变动的原因辞去董事职务，不再担任董事长及董事会战略与投资决策委员会主任职务。董事会提名孔庆伟顶替高国富为第八届董事会执行董事候选人。近日有媒体报导称，集团董事长孔庆伟将任党委书记一职，现任党委书记、董事长高国富任党委书记。（证券时报·e公司）"))
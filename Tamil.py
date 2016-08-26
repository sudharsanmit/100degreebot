class Tamil(object):
    def __init__(self,*args,**kwargs):
	    pass
		
    def uyir():
        return ['அ','ஆ','இ','ஈ','உ','ஊ','எ','ஏ','ஐ','ஒ','ஓ','ஔ','ஃ'];
    
    def mei_base():
        return ['க','ங','ச','ஞ','ட','ண','த','ந','ப','ம','ய','ர','ல','வ','ழ','ள','ற','ன'];
    
    def compose_uyir_mei():
        return ['','ா', 'ி', 'ீ', 'ு', 'ூ', 'ெ', 'ே', 'ை', 'ொ', 'ோ', 'ௌ']
    
    def compose_mei():
        return ['்']
    
    def uyir_kuril():
        return ['அ','இ','உ','எ','ஒ']
    
    def uyir_nedil():
        return ['ஆ','ஈ','ஊ','ஏ','ஐ','ஓ','ஔ']
    
    def compose_uyir_mei_kuril():
        return ['', 'ி', 'ு', 'ெ', 'ொ']
    
    def compose_uyir_mei_nedil():
        return ['ா', 'ீ', 'ூ', 'ே', 'ை', 'ோ', 'ௌ']
    
    def vallinam():
        return ['க','ச','ட','த','ப','ற']
    
    def mellinam():
        return ['ங','ஞ','ண','ந','ம','ன']
    
    def idaiyinam():
        return ['ய','ர','ல','வ','ழ','ள']
    
    def suttu():
        return ['அ','இ','உ']
    
    def um(f):
        result = []
        for i in mei_base():
            for j in f():
                result.append(i+j)
        return result
    
    def expand(symbol):
        result = []
        for i in mei_base():
            result.append(i+symbol)
        return result
    
    def varisai(symbol):
        result = []
        for i in compose_uyir_mei():
            result.append(symbol+i)
        return result
    
    def _is(f,symbol):
        try:
            if(1 + (f).index(symbol)):
                return True
        except ValueError:
            return False
        
    def uyir_mei():
        return um(compose_uyir_mei)
    
    def uyir_mei_kuril():
        return um(compose_uyir_mei_kuril)
    
    def uyir_mei_nedil():
        return um(compose_uyir_mei_nedil)
        
    def mei():
        return list(map(lambda x:x+'்',mei_base()))
    
    def is_kuril(symbol):
        return _is(uyir_kuril() + uyir_mei_kuril(),symbol)
                
    def is_nedil(symbol):
        return _is(uyir_nedil() + uyir_mei_nedil(),symbol)
    
    def is_mei(symbol):
        return _is(mei(),symbol)
    
    def is_mei_base(symbol):
        return _is(mei_base(),symbol)
    
    def is_compose_uyir_mei(symbol):
        return _is(compose_uyir_mei(),symbol)
    
    def is_compose_mei(symbol):
        return _is(compose_mei(),symbol)
    
    def is_letter(symbol):
        return _is(uyir() + mei() + uyir_mei(),symbol)
    
    # word needs to be passed as an array.
    def is_vina(word):
        result = False
        if word[:1] in ['எ','ஏ','யா'] + expand('ே'):
            result = True
        if word[-1] in ['ஆ','ஓ','ஏ',]+ expand('ோ') + expand('ே') + expand('ா'):
            result = True
        return result
    
    def is_slice_in_list(items,master):
        len_s = len(items) #so we don't recompute length of s on every iteration
        return any(items == master[i:len_s+i] for i in range(len(master) - len_s+1))
    
    def inaiezhuthu():
        result = []
        pairs = [['ஆ','அ'],['ஈ','இ'],['ஊ','உ'],['ஏ','எ'],['ஐ','இ'],['ஓ','ஒ'],['ஔ','உ']]
        for pair in pairs:
                result.append(pair)
        for idx,val in enumerate(uyir_mei_nedil()):
            result.append([val,result[idx][1]])
        return result
           
    def kuttriyalugaram(word):
        if len(word) == 1:
            return False
        if word[-1] in expand('ு'):
            return True
        else:
            return False
    
    def kuttriyaligaram(word):
        if len(word) == 1:
            return False
        for i in expand('ி'):
            for j in varisai('ய'):
                if(is_slice_in_list([i,j],word)):
                    return True
                else:
                    pass
        return False
                
    def ottralapedai(word):
        result = False
        for i in ['ங்', 'ஞ்', 'ண்', 'ந்', 'ம்', 'ன்', 'வ்', 'ய்', 'ல்', 'ள்', 'ஃ']:
            if (is_slice_in_list([i,i],word)):
                return True
            else:
                pass
        return False
    
    def uyiralapedai(word):
        result = False
        for i in inaiezhuthu():
            if (is_slice_in_list(i,word)):
                return True
            else:
                pass
        return False
                
    # symbol needs to be passed as a string
    def mathirai(symbol):
        print(uyir_mei_nedil() + uyir_nedil())
        print(uyir_mei_kuril() + uyir_kuril())
        if (symbol in mei()):
            return 0.5
        elif (symbol in uyir_mei_kuril() + uyir_kuril()):
            return 1
        elif (symbol in uyir_mei_nedil() + uyir_nedil()):
            return 2
        else:
            return 0
    
    def mudhal():
        result = []
        result = result + varisai('க') + varisai('ச') + varisai('த') + varisai('ந') + varisai('ப') + varisai('ம')
        for i in uyir():
            result.append(i)
        for i in ['', 'ா', 'ி', 'ீ', 'ெ', 'ே', 'ை', 'ௌ']:
            result.append('வ'+i)
        for i in ['', 'ா', 'ு', 'ூ', 'ோ', 'ௌ']:
            result.append('ய'+i)
        for i in ['', 'ா', 'ெ', 'ொ']:
            result.append('ஞ'+i)
        return result
    
    def irudhi():
        result = []
        for i in ['','ா', 'ி', 'ீ', 'ு', 'ூ', 'ெ', 'ே', 'ை', 'ொ', 'ோ', 'ௌ']:
            for j in mei_base():
                result.append(j+i)
        for i in ['ஞ்','ண்','ந்','ம்','ன்','ய்','ர்','வ்','ழ்','ள்']:
            result.append(i)
        return result
    
    #TODO: If kuttriyalugaram/ligaram - 0.5 Mathirai
    #TODO: If uyiralapedai - 3
    #TODO: If ottralapedai - 1
    #TODO: Aigarakurukkam
    #TODO: Ougarakurukkam
    #TODO: Magarakurukkam
    #TODO: Aiythakurukkam
    # TODO: Aiyadha ezhuthu inbetween kuril and uyir mei vallinam...
    def w2l(word):
        letters = []
        w = iter(range(len(word)))
        for i in w:
            if (is_letter(word[i:i+2])):
                letters.append(word[i:i+2])
                if (len(word) > i+2):
                    next(w)
                elif (len(word) == i+2):
                    break
                else:
                    pass
            else:
                letters.append(word[i:i+1])
        return letters
'''
print(uyir_mei())
print (mei())
print (is_kuril('த'))
print (is_mei('ந'))
print (w2l('கூறாதிருந்தானன்னன்ன்'))
print (is_vina(['கோ']))
print (mathirai('கே'))
#print (mathirai('தி'))
print (kuttriyalugaram(w2l('இரு')))
print (ottralapedai(w2l('இங்ரு')))
print (varisai('ய'))
print (kuttriyaligaram(w2l('சங்கியாது')))
print ((w2l('இன்றியமையாத')))
print (inaiezhuthu())
print (uyiralapedai(w2l('ஔஉ')))
print (mudhal())
print (irudhi())
'''
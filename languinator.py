import discord
from discord.ext import commands
import random
import abc
import xml.etree.ElementTree as ET
import numpy as np
import mysql.connector
from dataclasses import dataclass
from tabulate import tabulate
import re

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!lang ',intents=intents)


list_of_letters_from_romanian_alphabet='a,ă,â,b,c,d,e,f,g,h,i,î,j,k,l,m,n,o,p,q,r,s,ș,t,ț,u,v,w,x,y,z'.split(',')
dict_of_letters_from_romanian_alphabet={}
for idx,letter in enumerate(list_of_letters_from_romanian_alphabet):
    dict_of_letters_from_romanian_alphabet[letter]=idx

# the line(s) below has been omited for security reasons; this where the bot connects to the mySQL database where user and server information are stored
# mydb = mysql.connector.connect( {the user,pasword and name of the database} )
mycursor = mydb.cursor()


xp_up_to_date=False


@dataclass
class import_language_message_info:
    name_of_language_to_import:str
    guild_id_of_language_to_import:str
    guild_of_origin_id:str
    channel_of_origin:int
messages_to_admins_info=dict()




class phiNotImplementedException(Exception):
    pass

def phi(n) -> int :
    """ purpose:
        returns the value of the Euler totient function for a natural number n
        ( the number of natural numbers smaller than n that are coprime with n)

        parameters:
        -> n (int)
    """
    if n==26: return 12
    if n==27: return 18
    if n==13: return 12
    if n==31: return 30
    raise phiNotImplementedException




class cypher:
    @abc.abstractmethod
    def __call__(self, mesaj):
        pass

    @abc.abstractmethod
    def decode(self,message):
        pass

    @abc.abstractmethod
    def XMLformat(self, parent=None):
        pass

    @staticmethod
    def decode_XML(XMLelement):
        cypher_type=XMLelement.get('type')
        if cypher_type==None: raise Exception

        if cypher_type=='affineCypher':
            a_value=XMLelement.find('a')
            b_value=XMLelement.find('b')
            if a_value==None and b_value==None:raise Exception
            return affineCypher(int(a_value.text),int(b_value.text))

        elif cypher_type=='HillCypher':
            matrix_element=XMLelement.find('matrix')
            if matrix_element==None:raise Exception
            matrix=[]
            for line in matrix_element:
                matrix_line=eval('['+','.join([value for value in line.text.split(' ') if value!='']) +']')
                matrix.append(matrix_line)
            matrix=np.array(matrix,dtype='int16')
            return HillCypher(matrix)

        elif cypher_type=='VigenereCypher':
            key=XMLelement.find('key')
            if key==None: raise Exception
            return VigenereCypher(key.text)

    # @abc.abstractmethod
    # def call_appropriate_JSONEncoder(self):
    # pass


class tryToModify_inverse_a_Exception(Exception):
    pass

class affineCypher(cypher):
    def __init__(self, a, b):
        self._a = a
        self._inverse_a = 1
        for i in range(phi(31)-1): self._inverse_a = (self._inverse_a * a) % 31
        self._b = b
    def __repr__(self):
        return f'AFFINE CYPHER:[a:{self._a} ; b:{self._b}]'

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self,new_a):
        if isinstance(new_a,int):
            self._a=new_a
            self._inverse_a=1
            for i in range(phi(31) - 1): self._inverse_a = (self._inverse_a * new_a) % 31
        else:
            raise Exception

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self,new_b):
        if isinstance(new_b,int):
            self._b=new_b
        else:
            raise Exception

    @property
    def inverse_a(self):
        return self._inverse_a

    @inverse_a.setter
    def inverse_a(self,val):
        raise tryToModify_inverse_a_Exception

    def _encrypt_and_decrypt_affine_Cypher_template(self,message,expression) -> str:
        """
        purpose:

        parameters:
        ->message (string): the message to be encrypted/decrypted
        ->expression (function): a function that takes a single character an returns an integer between 0 and 30
        based on the given character; is used to determine the characters in the returned string
        """
        message_to_return=''
        star_in_efect=False
        for idx,char in enumerate(message):
            if char=='*' and message[idx-1]==' ' and message[idx+1]==' ': star_in_efect= not star_in_efect
            if char in dict_of_letters_from_romanian_alphabet.keys() and not star_in_efect:
                message_to_return += list_of_letters_from_romanian_alphabet[expression(char)]
            elif char.lower() in dict_of_letters_from_romanian_alphabet.keys() and not star_in_efect:
                message_to_return += list_of_letters_from_romanian_alphabet[expression(char.lower())].upper()
            else:
                message_to_return += char
        return message_to_return

    def __call__(self, message) -> str:
        expression= lambda char : (self._a * dict_of_letters_from_romanian_alphabet[char] + self._b) % 31
        return self._encrypt_and_decrypt_affine_Cypher_template(message, expression)

    def decode(self, message) -> str:
        expression= lambda char : (self._inverse_a * (dict_of_letters_from_romanian_alphabet[char] - self._b)) % 31
        return self._encrypt_and_decrypt_affine_Cypher_template(message, expression)

    def XMLformat(self, parent=None):
        """purpose:
           creates and returns an XML element containing information of the calling object and adds it to the DOM tree

           parameters:
           ->parent ( ET.Element/ET.SubElement ; optional ): if not None, it will be the element's parent in the DOM tree
           """
        if (parent == None):
            cypher_element = ET.Element('cypher')
        else:
            cypher_element = ET.SubElement(parent, 'cypher')
        cypher_element.set('type','affineCypher')
        a = ET.SubElement(cypher_element, 'a')
        a.text = str(self._a)
        b = ET.SubElement(cypher_element, 'b')
        b.text = str(self._b)
        return cypher_element

    #def call_appropriate_JSONEncoder(self):
        #encode_affineCypher(self)



class VigenereCypher(cypher):
    def __init__(self,key):
        self._key=key

    def _encrypt_and_decrypt_affine_Cypher_template(self, message, expression) -> str:
        message_to_return = ''
        star_in_efect = False
        key_len = len(self._key)
        for idx, char in enumerate(message):
            key_idx = idx % key_len
            if char == '*' and message[idx - 1] == ' ' and message[idx + 1] == ' ': star_in_efect = not star_in_efect
            if char in dict_of_letters_from_romanian_alphabet.keys() and not star_in_efect:
                message_to_return += list_of_letters_from_romanian_alphabet[expression(char,key_idx)]
            elif char.lower() in dict_of_letters_from_romanian_alphabet.keys() and not star_in_efect:
                message_to_return += list_of_letters_from_romanian_alphabet[expression(char.lower(),key_idx)].upper()
            else:
                message_to_return += char
        return message_to_return

    def __call__(self,message):
        expression= lambda char, key_idx : (dict_of_letters_from_romanian_alphabet[char] +
                                            dict_of_letters_from_romanian_alphabet[self._key[key_idx]]) % 31
        return self._encrypt_and_decrypt_affine_Cypher_template(message,expression)

    def decode(self,message):
        expression = lambda char, key_idx: (dict_of_letters_from_romanian_alphabet[char] -
                                            dict_of_letters_from_romanian_alphabet[self._key[key_idx]]) % 31
        return self._encrypt_and_decrypt_affine_Cypher_template(message,expression)

    def XMLformat(self, parent=None):
        if (parent == None):
            cypher_element = ET.Element('cypher')
        else:
            cypher_element = ET.SubElement(parent, 'cypher')
        cypher_element.set('type','VigenereCypher')
        key = ET.SubElement(cypher_element, 'key')
        key.text = self._key
        return cypher_element



class unableToFindPivotException(Exception):
    pass

def Gauss_elimination_modulo_p(matrix,p=31):
    """purpose:
       returns the inverse of a matrix modulo a prime number

       parameters:
       ->matrix (numpy array) : the matrix to be inverted
       ->p ( int ; optional ) : the prime number for which the modulo will be calculated;
       the default is 31; WARNING: calls phi(p)"""

    if len(matrix.shape)!=2 or matrix.shape[0]!=matrix.shape[1]: raise Exception
    matrix_size=matrix.shape[0]
    matrix=matrix % p
    inverse_matrix=np.identity(matrix_size,dtype='int32')
    for k in range(matrix_size):
        piv_idx_lin=k
        piv_idx_col=k
        while matrix[piv_idx_lin][k]==0:
            if piv_idx_lin<matrix_size-1:
                piv_idx_lin+=1
            elif piv_idx_col<matrix_size-1:
                piv_idx_col+=1
                piv_idx_lin=k
            else:
                raise unableToFindPivotException
        matrix[k],matrix[piv_idx_lin]=matrix[piv_idx_lin],matrix[k]
        inverse_matrix[k],inverse_matrix[piv_idx_lin]=inverse_matrix[piv_idx_lin],inverse_matrix[k]
        piv_inv_matrix = 1
        for i in range(phi(p) - 1):
            piv_inv_matrix = (piv_inv_matrix * matrix[k][k]) % p
        matrix[k]=(matrix[k]*piv_inv_matrix) % p
        inverse_matrix[k]=(inverse_matrix[k]*piv_inv_matrix) % p

        for i in range(k+1,matrix_size):
            if matrix[i][k]==0:continue
            else:
                aux=matrix[i][k]
                matrix[i]=(matrix[i] - aux * matrix[k]) % p
                inverse_matrix[i] = (inverse_matrix[i] - aux * inverse_matrix[k]) % p
    for k in range(matrix_size-1,-1,-1):
        for i in range(k):
            if matrix[i][k]==0:continue
            else:
                aux=matrix[i][k]
                matrix[i] = (matrix[i] - aux * matrix[k]) % p
                inverse_matrix[i] = (inverse_matrix[i] - aux * inverse_matrix[k]) % p
    return inverse_matrix


#Hill_dict=dict_of_letters_from_romanian_alphabet
#Hill_dict.pop()

def apply_HillCypher(matrix,message) -> str :
    """
    purpose:
    serves as a template for both the __call__ and decrypt methods within the HillCypher class;

    parameters:
    -> matrix (numpy array):
    ->message (string): the message to be encrypted/decrypted
    """
    list_of_words=re.findall(r"[\w*]+",message)
    coded_message=''
    matrix_dim=matrix.shape[0]
    star_in_efect= False
    for word in list_of_words:
        if word=='*':
            star_in_efect= not star_in_efect
            coded_message += "* "
            continue
        if star_in_efect: coded_message += word + ' '
        else:
            word_len=len(word)
            for idx in range(0,word_len,matrix_dim):
                letter_is_upper=[False if letter == letter.lower() else True for letter in word[idx:idx+matrix_dim]] + (matrix_dim-(word_len-idx-1))*[False]
                letter_codes=[dict_of_letters_from_romanian_alphabet[letter] if letter == letter.lower()
                              else dict_of_letters_from_romanian_alphabet[letter.lower()]
                              for letter in word[idx:idx+matrix_dim]]
                if word_len-idx<matrix_dim:
                    letter_codes+=[30]*(matrix_dim -(word_len -idx))
                letter_codes_vector=np.array(letter_codes,dtype='int16')
                coded_letters_vector= np.matmul(letter_codes_vector , matrix) % 31
                coded_letters=[list_of_letters_from_romanian_alphabet[letter_code] if not letter_is_upper[idx]
                               else list_of_letters_from_romanian_alphabet[letter_code].upper()
                               for idx,letter_code in enumerate(coded_letters_vector)]
                coded_message+=''.join(coded_letters)
            coded_message+=' '
    return coded_message


class tryToModify_inverse_matrix_Exception(Exception):
    pass

class HillCypher(cypher):
    def __init__(self,matrix):
        self._matrix=matrix
        self._matrix_inverse=Gauss_elimination_modulo_p(matrix,31)

    def __call__(self,message):
        return apply_HillCypher(self._matrix,message)

    def __repr__(self):
        return f'HILL CYPHER:[matrix:{self._matrix}]'

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self,matrix):
        if type(matrix)==type(np.array()):
            self._matrix=matrix
            self._matrix_inverse = Gauss_elimination_modulo_p(matrix, 31)
        else:
            raise Exception
    @property
    def matrix_inverse(self):
        return self._matrix_inverse

    @matrix_inverse.setter
    def matrix_inverse(self,val):
        raise tryToModify_inverse_matrix_Exception

    def decode(self,message):
        return apply_HillCypher(self._matrix_inverse,message)

    def XMLformat(self, parent=None):
        if (parent == None):
            cypher_element = ET.Element('cypher')
        else:
            cypher_element = ET.SubElement(parent, 'cypher')
        cypher_element.set('type','HillCypher')
        matrix = ET.SubElement(cypher_element, 'matrix')
        matrix_text=(str(self._matrix).splitlines())
        for matrix_line in matrix_text:
            matrix_line=matrix_line.strip(' []')
            line=ET.SubElement(matrix,'line')
            line.text=matrix_line




def generate_cypher(cypher_type='affine') ->cypher :
    """purpose:
       returns an object of the subclass of cypher that corresponds to cypher_type, initialized with random parameters

       parameters:
       ->cypher_type ( string ; optional ): specifies the type of the cypher object that will be created;
       must correspond to the name of a subclass of cypher; the default is affine
       """
    if (cypher_type.strip().lower() == 'affine'):
        a = random.randint(2, 30)
        b = random.randint(2, 30)
        return affineCypher(a, b)
    if cypher_type.strip().lower()== 'hill':
        n = random.randint(2, 4)
        matrix = np.random.randint(31, size=(n, n), dtype='int16')
        while (np.linalg.det(matrix) % 31 == 0):
            matrix = np.random.randint(31, size=(n, n), dtype='int16')
        try:
            return HillCypher(matrix)
        except unableToFindPivotException:
            return generate_cypher(cypher_type)
    if cypher_type.strip().lower()== 'vigenere':
        n=random.randint(5,10)
        key=''.join(random.sample(list_of_letters_from_romanian_alphabet,n))
        return VigenereCypher(key)




class languageExistsException(Exception):
    pass

class tryToModify_list_of_all_languages_Exception(Exception):
    pass

class language:
    list_of_all_languages = dict()
    levels_of_fluency=['beginner','intermediate','advanced']

    xp_to_attain_level_of_fluency=[10000,200000,5000000]

    def __init__(self, name, guild_id, cypher=None):
        name = name.strip().lower()
        if (name,guild_id) not in language.list_of_all_languages:
            self._name = name
            self._guild_id=guild_id
            if cypher != None:
                self._cypher = cypher
            else:
                self._cypher = generate_cypher()
            self._title_of_speaker = 'vorbitor de ' + name
            language.list_of_all_languages[(name,guild_id)] = self
            language.write_languages_to_XML()
            print(f'Am construit limba {name} si am adaugat-o la dictionar!')
        else:
            raise languageExistsException

    def __repr__(self):
        return f'LANGUAGE: [name: {self._name} ; cypher: {self._cypher}] .'

    def __call__(self, message):
        return self._cypher(message)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,new_name):
        if type(new_name)==str:
            del language.list_of_all_languages[(self._name,self._guild_id)]
            self._name=new_name
            language.list_of_all_languages[(new_name,self._guild_id)]=self
            language.write_languages_to_XML()
        else:
            raise Exception

    @property
    def cypher(self):
        return self._cypher

    @cypher.setter
    def cypher(self,new_cypher):
        if isinstance(new_cypher,cypher):
            self._cypher=new_cypher
        else:
            raise Exception

    def titles_of_speakers(self) -> tuple :
        return tuple( 'vorbitor de ' + self.name + ': '+ level for level in language.levels_of_fluency)

    @staticmethod
    def decode_XML(XMLelement) :
        """
        purpose:
        interprets an XML element containing language information
        and uses it to construct a language object, which is returned

        parameters:
        ->XMLelement ( ET.Element/ ET.SubElement ): the element in question
        """
        if XMLelement.tag != 'language': raise Exception
        language_name = XMLelement.get('name')
        guild_id=XMLelement.get('guild_id')
        if language_name == None or guild_id==None: raise Exception
        if XMLelement.find('cypher') == None: raise Exception
        language_cypher = cypher.decode_XML(XMLelement.find('cypher'))
        return language(language_name,guild_id, language_cypher)

    @staticmethod
    def decode_language_file(language_file):
        """
        purpose:
        reads from an .xml file containing a list of languages and constructs said languages,
        which will automatically add them to _list_of_all_languages

        parameters:
        ->language_file (string): the name of .xml file that will be read from
        """
        DOM_tree = ET.parse(language_file)
        list_of_all_languages_DOM_tree = DOM_tree.getroot()
        try:
            for element in list_of_all_languages_DOM_tree:
               language.decode_XML(element)
        except:
            print('Language file not valid!')

    @staticmethod
    def write_languages_to_XML():
        """
        purpose:
        writes the information for all languages in _list_of_all_languages to an .xml file

        parameters: None
        """
        list_of_languages = ET.Element('languages')
        language_file = open("list_of_languages.xml", "wb+")
        for lang in language.list_of_all_languages.values():
            language_to_add = ET.SubElement(list_of_languages, 'language')
            language_to_add.set('name', lang._name)
            language_to_add.set('guild_id',lang._guild_id)
            lang._cypher.XMLformat(language_to_add)
        languages_XML_string = ET.tostring(list_of_languages)
        language_file.write(languages_XML_string)




async def handle_fluency_level_up(user_id,guild,language_name,current_xp):
    """
    purpose:
    determines whether a user qualifies for a level-up in fluency for the specified language
    based on the current xp amount;  if he does, the appropriate role
    will be given to him within the guild

    parameters:
    ->user_id (string): the id of the user in question
    ->guild (discord guild object): an object representing the guild in question
    ->language_name (string): the name of the language
    ->current_xp (int): the user's current xp amount for that particular language
    """
    global xp_up_to_date
    if not xp_up_to_date:
        number_of_levels_of_fluency=len(language.levels_of_fluency)
        for i in range(number_of_levels_of_fluency-1,-1,-1):
            if current_xp >= language.xp_to_attain_level_of_fluency[i]:
                current_language=language.list_of_all_languages[(language_name,str(guild.id))]
                member=guild.get_member(user_id)
                role_title=current_language.titles_of_speakers()[i]
                role_names=[role.name for role in guild.roles]
                role=guild.roles[role_names.index(role_title)]
                if role not in member.roles:
                    xp_up_to_date=True
                    await member.add_roles(role)
                break
    else: xp_up_to_date=False




#                                   SQL TABLE RELATED FUNCTIONS
########################################################################################################################
class entryDoesNotExistException(Exception):
    pass

def get_experience_from_user_fluency_table(user_id,guild_id,language_name) -> int :
    sql = f"SELECT experience FROM user_fluency_table " \
          f"WHERE user_id='{user_id}' AND " \
          f"guild_id='{guild_id}' AND " \
          f"language_name='{language_name}'; "
    mycursor.execute(sql)
    query_result = mycursor.fetchall()
    if len(query_result)==0:
        raise entryDoesNotExistException
    else:
        return query_result[0][0]

async def insert_entry_into_user_fluency_table(user_id,guild,language_name,xp_value):
    sql = f"INSERT INTO user_fluency_table (user_id,guild_id,language_name,experience) " \
          f"VALUES ('{user_id}','{guild.id}','{language_name}',{xp_value}); "

    mycursor.execute(sql)
    mydb.commit()
    await handle_fluency_level_up(user_id,guild,language_name,xp_value)

def delete_language_entries_from_user_fluency_table(guild_id,language_name):
    sql = f"DELETE FROM user_fluency_table " \
          f"WHERE guild_id='{guild_id}'AND language_name ='{language_name}' ; "

    mycursor.execute(sql)
    mydb.commit()

async def update_experience_in_user_fluency_table(user_id,guild,language_name,new_xp_value):

    sql = f"UPDATE user_fluency_table " \
          f"SET experience={new_xp_value} " \
          f"WHERE user_id='{user_id}' AND " \
          f"guild_id='{guild.id}' AND " \
          f"language_name='{language_name}'; "

    mycursor.execute(sql)
    mydb.commit()
    await handle_fluency_level_up(user_id, guild, language_name, new_xp_value)

def insert_entry_into_guild_table(guild_id,guild_name):
    sql=f"INSERT INTO guild_table (guild_id,guild_name) " \
    f"VALUES ('{guild_id}','{guild_name}') ; "
    mycursor.execute(sql)
    mydb.commit()

def remove_entry_from_guild_table(guild_id):
    sql=f"DELETE FROM guild_table " \
        f"WHERE guild_id='{guild_id}' ; "
    mycursor.execute(sql)
    mydb.commit()
########################################################################################################################




#                                     BOT EVENTS
########################################################################################################################
@bot.event
async def on_ready():
    print("The bot is ready!")
    name = "with words"
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name))

@bot.event
async def on_guild_join(guild):
    insert_entry_into_guild_table(guild.id,guild.name)

@bot.event
async def on_guild_remove(guild):
    remove_entry_from_guild_table(guild.id)

def list_difference(list1,list2):
    return list(set(list1) - set(list2))

@bot.event
async def on_member_update(before,after):
    if len(before.roles)<len(after.roles):
        new_roles=list_difference(after.roles,before.roles)
        new_speaker_roles=[role for role in new_roles if 'vorbitor de ' in role.name]
        old_speaker_roles=[role for role in before.roles if 'vorbitor de ' in role.name]
        for new_role in new_speaker_roles:
            name=new_role.name
            language_name=name[len('vorbitor de '):name.find(':')]
            fluency_level=name[name.find(':')+2:]
            to_display='Congratulations, <@'+ str(after.id) + '>! You are now an '
            to_display+= fluency_level + ' speaker of ' + language_name
            await after.guild.text_channels[-1].send(to_display)
            for old_role in old_speaker_roles:
                if old_role.name[len('vorbitor de '):old_role.name.find(':')]==new_role.name[len('vorbitor de '):new_role.name.find(':')]:
                    await after.remove_roles(old_role)

            global xp_up_to_date
            if not xp_up_to_date:
                user_id=after.id
                guild=after.guild
                fluency_leveL_index=language.levels_of_fluency.index(fluency_level)
                xp_value = language.xp_to_attain_level_of_fluency[fluency_leveL_index]
                exception_raised=False
                xp_up_to_date=True
                try:
                    get_experience_from_user_fluency_table(user_id,guild.id,language_name)
                except entryDoesNotExistException:
                    await insert_entry_into_user_fluency_table(user_id,guild,language_name,xp_value)
                    exception_raised=True

                if not exception_raised:
                    await update_experience_in_user_fluency_table(user_id,guild,language_name,xp_value)
            else: xp_up_to_date=False

@bot.event
async def on_raw_reaction_add(payload):
    message_id=payload.message_id
    if message_id in messages_to_admins_info:
        if payload.emoji.name == '👍' or payload.emoji.name=='👎':
            for channel in bot.private_channels:
                if payload.channel_id == channel.id:
                    channel_of_message = channel
                    break
            message = channel_of_message.get_partial_message(message_id)
            await message.edit(content="Your decision has been noted!",delete_after=10)
            channel_of_origin = bot.get_channel(int(messages_to_admins_info[message_id].channel_of_origin))

            language_name = messages_to_admins_info[message_id].name_of_language_to_import
            if payload.emoji.name == '👍':
                guild_to_import_from_id = messages_to_admins_info[message_id].guild_id_of_language_to_import
                cypher_to_import = language.list_of_all_languages[(language_name, guild_to_import_from_id)].cypher
                guild_of_origin_id=messages_to_admins_info[message_id].guild_of_origin_id
                language.list_of_all_languages[(language_name,guild_of_origin_id)].cypher=cypher_to_import
                await channel_of_origin.send(f"Your request of importing the '{language_name}' language has been approved.")

            elif payload.emoji.name=='👎' :
                await channel_of_origin.send(f"Your request of importing the '{language_name}' language has been denied.")


########################################################################################################################




class languageDoesNotExistException(Exception):
    pass

def check_if_member_speaks_language(member,language_name):
    language_name = language_name.lower().strip()
    guild_id=str(member.guild.id)
    if (language_name, guild_id) in language.list_of_all_languages.keys():
        language_of_message = language.list_of_all_languages[(language_name,guild_id)]
        for role in member.roles:
            if role.name in language_of_message.titles_of_speakers():
                return True
        return False
    else: raise languageDoesNotExistException

async def encrypt_and_decrypt_command_template(ctx,message,language_name,string_to_display,send_privately,xp_modifier=1):
    try:
        if check_if_member_speaks_language(ctx.message.author,language_name):
            if send_privately:
                await ctx.message.author.send(string_to_display)
            else:
                await ctx.send(string_to_display)
            author_id=ctx.message.author.id
            current_xp_value=get_experience_from_user_fluency_table(author_id,ctx.guild.id,language_name)
            new_xp_value= current_xp_value + max(1,xp_modifier*len(message))
            await update_experience_in_user_fluency_table(author_id,ctx.guild,language_name,new_xp_value)
        else:
            await ctx.send('You do not know that language!')
    except languageDoesNotExistException:
        await ctx.send('The language does not exist!')
    except:
        await ctx.send('An error has occurred! Please contact the developer.')




#                                                BOT COMMANDS
########################################################################################################################
@commands.command(pass_context=True)
async def clean(ctx, limit: int = None, display_msg: bool = True, purge: bool = True):
    """(discord command)

        purpose:
        deletes a specified number of messages from the channel where the command was called;
        the messages deleted are the last ones in chronological order;
        the user using this command must have administrator privileges for it work

        parameters:
        ->limit (int) : the number of messages to be deleted;
        ->display_msg (bool): specifies whether a message should be displayed on the channel
        after the messages have been deleted;
    """
    passed = 0
    failed = 0
    if ctx.message.author.guild_permissions.administrator:
        if (purge == True):
            await ctx.channel.purge(limit=limit)
            if (display_msg == True):
                await ctx.send(f"Purged {limit} messages")
        else:
            async for msg in ctx.message.channel_history(limit=limit):
                try:
                    await msg.delete()
                    passed += 1
                except:
                    failed += 1
                await ctx.send(f"Removed {passed} messages with {failed} fails")

@commands.command()
async def encrypt(ctx, message, language_name):
    """(discord command)

       purpose:
       encrypt a message in an already existing LANGuinator 'language';
       the user must know the 'language' in order to encrypt it;
       this command will delete the message calling it and post the encrypted message on
       the channel where it was called

        parameters:
        -> message (string): message to be encrypted
        -> language_name (string): the name of the 'language' with which
        the message will be encrypted ( must be present in the database )
    """
    await clean(ctx, 1, False)
    if (language_name, str(ctx.guild.id)) in language.list_of_all_languages:
        string_to_display="Mesajul tau a fost criptat in limba '" + language_name + "', acela fiind: ```"
        string_to_display += language.list_of_all_languages[(language_name,str(ctx.guild.id))](message) + '```'
        await encrypt_and_decrypt_command_template(ctx,message,language_name,string_to_display,False)
    else:
        await ctx.send('The language does not exist!')

@commands.command()
async def decrypt(ctx, message, language_name):
    """(discord command)

       purpose:
       decrypt a message written in a LANGuinator 'language';
       the user must know the 'language' in order to decrypt it;
       the decrypted message will be sent privately to the user calling this command

        parameters:
        -> message (string): the message to be decrypted
        -> language_name (string): the name of the 'language'
        in which the message is ( presumed to have been ) written
    """
    if (language_name, str(ctx.guild.id)) in language.list_of_all_languages:
        string_to_display = 'Mesajul tau a fost decriptat, acela fiind: ```'
        string_to_display += language.list_of_all_languages[(language_name,str(ctx.guild.id))].cypher.decode(message) + '```'
        await encrypt_and_decrypt_command_template(ctx,message,language_name,string_to_display,True,200000)
    else:
        await ctx.send('The language does not exist!')



#@commands.command()
async def add_language_roles_to_server(ctx,language_name):
    """(discord command)

        purpose:
        creates a number of roles equal to the number of fluency levels;
        these roles will be used to determine fluency for the specified 'language';
        requires administrator privileges

        parameters:
        ->language_name (string) : the name of the 'language' associated with the roles to be created
    """
    if ctx.message.author.guild_permissions.administrator:
        title_of_speaker=language.list_of_all_languages[(language_name,str(ctx.guild.id))]._title_of_speaker
        to_display="The following roles have been added to the server:```"
        for level in language.levels_of_fluency:
            role_name=title_of_speaker + ': ' + level
            await ctx.guild.create_role(name=role_name)
            to_display += role_name + ' ; '
        to_display += '```'
        await ctx.send(to_display)
    else:
        await ctx.send('You do not have permission to perform that action!')


@commands.command()
async def create_language(ctx, language_name, cypher_type=None):
    """(discord command)

       purpose:
       create a LANGuinator 'language' with a randomly initialized cypher
       ( the type of cypher can be specified); if a 'language' with that name
       already exists within the server, an appropriate error message will be displayed;
       requires administrator privileges

        parameters:
        -> language_name (string):  the name of the newly created 'language'
        ->cypher_type ( string ; optional ): the type of cypher that the new 'language'
        will use to encrypt/decrypt messages; the default is an affine Cypher
    """
    if ctx.message.author.guild_permissions.administrator:
        try:
            if cypher_type!=None:
                cypher=generate_cypher(cypher_type)
                language(language_name,str(ctx.guild.id),cypher)
            else:
                language(language_name,str(ctx.guild.id))
            await ctx.send(f"The '{language_name}' language was successfully created for use within this server.")
            await add_language_roles_to_server(ctx,language_name)
        except languageExistsException:
            await ctx.send(f"The language already exists !")
        except:
            await ctx.send('An error has occurred! Please contact the developer.')
    else:
        await ctx.send('You do not have permission to perform that action!')


@commands.command()
async def delete_language(ctx,language_name):
    """(discord command)
        deletes the language with the specified name from the server,
        as well as its associated roles; requires administrator privileges

        parameters:
    -   >language_name (string): the name of the language to be deleted
    """
    if (language_name,str(ctx.guild.id)) in language.list_of_all_languages.keys():
        deleted_language=language.list_of_all_languages.pop((language_name,str(ctx.guild.id)))
        language.write_languages_to_XML()
        for role in ctx.guild.roles:
            if role.name in deleted_language.titles_of_speakers():
                await role.delete()
        delete_language_entries_from_user_fluency_table(ctx.guild.id,language_name)
        await ctx.send(f"The '{language_name}' language was deleted from the server.")
    else:
        await ctx.send("There is no language with that name within the server!")


def name_of_language(lang):
    return lang.name

@commands.command()
async def display_language_names(ctx):
    """(discord command)

        purpose:
        display all the names of the 'languages' present in the database for the server
        where the command was issued

        parameters: None
    """
    to_display=" 'Language' names present in the database:```\n"
    for lang in sorted(language.list_of_all_languages.values(),key=name_of_language):
        if lang._guild_id == str(ctx.guild.id):
            to_display+=lang.name+'\n'
    to_display+='```'
    await ctx.send(to_display)

@commands.command()
async def send_my_xp_status(ctx):
    """(discord command)

        purpose:
        sends the user calling this command a private message with information regarding
        the amount of xp until the next fluency level-up for each 'language' within each server;
        the information is displayed in the form of a table

        parameters: None
    """
    user_id=ctx.message.author.id
    sql=f"SELECT g.guild_name,g.guild_id,uf.language_name,uf.experience " \
        f"FROM user_fluency_table as uf " \
        f"INNER JOIN guild_table as g " \
        f"ON uf.guild_id=g.guild_id " \
        f"WHERE uf.user_id='{user_id}' ;"
    mycursor.execute(sql)
    table_rows=[list(row) for row in mycursor.fetchall()]
    number_of_levels_of_fluency = len(language.levels_of_fluency)
    for row in table_rows:
        xp_value=row[-1]
        for i in range(number_of_levels_of_fluency - 1, -1, -1):
            if xp_value >= language.xp_to_attain_level_of_fluency[i]:
                row.insert(-2,language.levels_of_fluency[i])
                if i < number_of_levels_of_fluency - 1:
                    row[-1]=language.xp_to_attain_level_of_fluency[i+1]- xp_value
                else:
                    row[-1]='-'
                break
    to_send = tabulate(table_rows,headers=["Guild_name","Guild_id","Language_name","Fluency_level","Xp_till_next_level"],stralign="center")
    await ctx.message.author.send(to_send)

@commands.command()
async def import_language(ctx,language_name,guild_id):
    """(discord command)

        purpose:
        initiates a request to import the 'language' with the given name from the given server;
        the request will be sent to the server's admins; if it is approved by one of the admins,
        the language cypher will be imported; in its current implementation,
        the command requires the language to be created beforehand

        parameters:
        ->language_name (string) : the name of the language to be imported;
        ->guild_id (alphanumeric string): the id of the guild to import from;
        """
    if (language_name,guild_id) in language.list_of_all_languages:
        if (language_name,str(ctx.guild.id)) in language.list_of_all_languages:
            guild_to_import_from=bot.get_guild(int(guild_id))
            administrators=[member for member in guild_to_import_from.members if member.guild_permissions.administrator and not member.bot]
            for admin in administrators:
                message_text=f"A request has been made from the server '{ctx.guild.name}', ID {ctx.guild.id} ," \
                             f" to import the cypher for language '{language_name}' from the server '{admin.guild.name}', ID {admin.guild.id} .\n" \
                             f"Reply to this message with a thumbs-up to approve it or thumbs-down to deny it. "
                messages_to_admins_info[(await admin.send(message_text)).id]=\
                    import_language_message_info(language_name,guild_id,str(ctx.guild.id),ctx.channel.id)

            message_text=f"Your request has been sent to the administrators of the server with the ID {guild_id} ." \
                             f" You will be notified if the request is approved or denied."
            await ctx.send(message_text)
        else:
            await ctx.send("Please create the language before importing!")
    else:
        await ctx.send("No language with that name exists within the given server!")

@commands.command()
async def chelp(ctx,command_name=None):
    """(discord command)

        purpose:
        displays either the names of all commands or the docstring for a particular command,
        depending on whether or not a value was given to the 'command_name' parameter

        parameters:
        -> command_name ( string ; optional ) : the name of command which the user wants to know more about;
        if no value is given the names of all commands will be displayed instead
    """
    if command_name==None:
        to_display = "LANGuinator Discord Bot by Cerbulescu Barbu-Ion \n\n Available commands:```\n"
        to_display +='\n'.join(sorted(list(command.name for command in bot.walk_commands()))) + "``` \n"
        to_display += "Use '!lang chelp (command_name)' " \
                   "to find what the command (command_name) does and how to use it. "
        await ctx.send(to_display)
    else:
        found_command_name=False
        for command in bot.walk_commands():
            if command.name==command_name:
                found_command_name=True
                await ctx.send("the '" + command_name + "' command:```" + command.help + '```')
                break
        if found_command_name==False:
            await ctx.send("There is no command with that name! Use '!lang chelp' to get all command names.")
########################################################################################################################



def main():
    language_file = open("list_of_languages.xml", "rb+")
    language.decode_language_file(language_file)

    bot.add_command(display_language_names)
    bot.add_command(encrypt)
    bot.add_command(decrypt)
    bot.add_command(clean)
    bot.add_command(chelp)
    bot.add_command(create_language)
    #bot.add_command(add_language_roles_to_server)
    bot.add_command(send_my_xp_status)
    bot.add_command(import_language)
    bot.add_command(delete_language)
    # the line below has been omited for privacy and security reasons; this where the token for the bot is given
    # token = { the token of the bot }
    bot.run(token)

if __name__ == "__main__":
    main()




"""
                                 UNUSED FUNCTIONS FOR .json ENCODING/DECODING
########################################################################################################################
def encode_cypher(cypherObject):
    cypherObject.call_appropriate_JSONEncoder()


def decode_cypher(dict):
    if type(dict) == type({}):
        if "object_type" in dict.keys():
            if dict["object_type"] == 'affineCypher':
                decode_affineCypher(dict)


def encode_affineCypher(cypherObject):
    if isinstance(cypherObject, affineCypher):
        return {"object_type": "affineCypher", "a": cypherObject.a, "b": cypherObject.b}
    else:
        type_name = cypherObject.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def decode_affineCypher(dict, conditionsChecked=False):
    if type(dict) == ({}):
        if "object_type" in dict.keys():
            if dict["object_type"] == "affineCypher":
                return affineCypher(dict['a'], dict['b'])


def encode_language(lang):
    print('In encode_language')
    print(f'In encode_language:{type(lang)}')
    if isinstance(lang, language):
        return list({"object_type": "language", "name": {lang.name}, "cypher": encode_cypher(lang.cypher)})
    else:
        type_name = lang.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def decode_language(dict):
    if type(dict) == {}:
        if "object_type" in dict.keys():
            if dict["object_type"] == "language":
                return language(dict["name"], decode_cypher(dict["cypher"]))
    return dict
########################################################################################################################
"""

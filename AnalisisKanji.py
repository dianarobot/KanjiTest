#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Diana Rocha Botello
"""
import JapaneseTokenizer
import json
import re

class AnalisisKanji():
	def __init__(self):
		self.mecab_wrapper = JapaneseTokenizer.MecabWrapper(dictType='ipadic')
		self.n5KanjiListFrecuencias = {}
		self.n5KanjiListWords = {}
		self.n5KanjiWords = {}

	def cleanFile(self):
		findTextTitle=0
		savedLine = 0
		file = 'jawiki-latest-pages-articles-multistream.xml'
		newFile = open("jawiki_clean.txt",'w', encoding='utf8')
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				savedLine = 0
				regex1 = re.compile(".*</text>.*")
				regex2 = re.compile(".*<title>.*")
				result = re.findall(regex2, line)
				if len(result)>0:
					newFile.write(line)
					findTextTitle = 0
					savedLine = 1
					print(line)
				if line.startswith('      <text xml:space="preserve">') or findTextTitle==1:
					findTextTitle = 1
					savedLine = 1	
					newFile.write(line)
					print(line)
				
				result = re.findall(regex1, line)
				if len(result)>0:
					findTextTitle = 0
					if savedLine == 0:	
						newFile.write(line)
						print(line)	
			f.close()
		newFile.close()

	def shortFileKanji(self):
		file = 'jawiki_clean.txt'
		newFile = open("jawiki_clean_shortVersion.txt",'w', encoding='utf8')
		articleNumber = 0
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				regex2 = re.compile(".*<title>.*")
				result = re.findall(regex2, line)
				if len(result)>0:
					articleNumber +=1
					print("ARTICLE NUMBER")
					print(articleNumber)
				if(articleNumber<50001):
					newFile.write(line)
			f.close()
		newFile.close()

	def saveJSON(self, filename, dictionary):
		with open(filename, 'w', encoding='utf8') as fp:
			json.dump(dictionary, fp, sort_keys=True, indent=4)
			fp.close()

	def readJSON(self, filename):
		with open(filename, 'r', encoding='utf8') as fp:
			if filename == 'frecuenciasN5.json':
				self.n5KanjiListFrecuencias = json.load(fp)
			else:
				self.n5KanjiListWords = json.load(fp)
			fp.close()

	def kanjiDictionaryFrecuencias(self):
		file = 'N5KanjiList.txt'
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				line = line.strip('\n')
				self.n5KanjiListFrecuencias.update({line:0})
			f.close()

	def frecuenciasSimples(self):
		self.kanjiDictionaryFrecuencias()
		file = 'jawiki_clean_shortVersion.txt'
		articleNumber = 0
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				regex2 = re.compile(".*<title>.*")
				result = re.findall(regex2, line)
				if len(result)>0:
					articleNumber +=1
				for kanji in self.n5KanjiListFrecuencias:
					counter = line.count(kanji)
					if counter > 0:
						value = self.n5KanjiListFrecuencias.get(kanji, 0)
						value +=counter
						self.n5KanjiListFrecuencias.update({kanji:value})
			f.close()
		print(self.n5KanjiListFrecuencias)
		self.saveJSON('frecuenciasN5.json', self.n5KanjiListFrecuencias)

	def kanjiDictionaryWords(self):
		file = 'N5KanjiList.txt'
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				line = line.strip('\n')
				self.n5KanjiListWords.update({line:{}})


	def KanjiWords(self):
		self.kanjiDictionaryWords()
		file = 'jawiki_clean_shortVersion.txt'
		articleNumber = 0
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				regex2 = re.compile(".*<title>.*")
				result = re.findall(regex2, line)
				if len(result)>0:
					articleNumber +=1
					print("ARTICLE NUMBER")
					print(articleNumber)
				# ipadic is well-maintained dictionary #
				tokens = self.mecab_wrapper.tokenize(line).convert_list_object()
				for token in tokens:
					for kanji in self.n5KanjiListWords:
						counter = token.count(kanji)
						if counter > 0:
							dictionaryWords = self.n5KanjiListWords.get(kanji, -1)
							wordValue = dictionaryWords.get(token, -1)
							if wordValue == -1:
								dictionaryWords.update({token: counter})
							else:
								wordValue += counter
								dictionaryWords.update({token: wordValue})	
							self.n5KanjiListWords.update({kanji:dictionaryWords})
			f.close()
		self.saveJSON('frecuenciasWordsN5.json', self.n5KanjiListWords)

	def KanjiFrecuenciasMayorMenor(self):
		self.readJSON('frecuenciasN5.json')
		self.n5KanjiListFrecuencias = sorted(self.n5KanjiListFrecuencias.items(), key=lambda item: item[1], reverse=True)
		print(self.n5KanjiListFrecuencias)

	def WordsForKanji(self):
		self.readJSON('frecuenciasWordsN5.json')
		self.n5KanjiWords = {}
		for kanji in self.n5KanjiListWords:
			dictionaryWords = self.n5KanjiListWords.get(kanji, -1)
			self.n5KanjiWords.update({kanji:len(dictionaryWords.keys())})
		self.n5KanjiWords = sorted(self.n5KanjiWords.items(), key=lambda item: item[1], reverse=True)
		print(self.n5KanjiWords)

	def frecuenciasPalabrasByKanji(self, max):
		self.readJSON('frecuenciasWordsN5.json')
		self.n5KanjiWords = {}
		for kanji in self.n5KanjiListWords:
			dictionaryWords = self.n5KanjiListWords.get(kanji, -1)
			dictionaryWords = sorted(dictionaryWords.items(), key=lambda item: item[1], reverse=max)
			i=0
			topTen = {}
			for w in dictionaryWords:
				i+=1
				if i < 11:
					topTen.update({(w[0]):(w[1])})
				else:
					break
			self.n5KanjiWords.update({kanji:topTen})
		print(self.n5KanjiWords)

	def frecuenciasPalabrasN5(self, max):
		self.readJSON('frecuenciasWordsN5.json')
		self.n5KanjiWords = {}
		for kanji in self.n5KanjiListWords:
			dictionaryWords = self.n5KanjiListWords.get(kanji, -1)
			dictionaryWords = sorted(dictionaryWords.items(), key=lambda item: item[1], reverse=max)
			for w in dictionaryWords:
				self.n5KanjiWords.update({(w[0]):(w[1])})
		self.n5KanjiWords = sorted(self.n5KanjiWords.items(), key=lambda item: item[1], reverse=max)	
		print(self.n5KanjiWords)


if __name__ == "__main__":
	ak= AnalisisKanji()
	#ak.cleanFile() #Crea un archivo con sólo títulos y artículos
	#ak.shortFileKanji() #Crea archivo con 50,000 artículos
	#ak.frecuenciasSimples() # Conteo de frecuencias para kanjis N5
	#ak.KanjiWords() # Frecuencias por palabra de cada kanji

	#### NECESITA LOS JSON  PARA REALIZAR ESTAS FUNCIONES ####
	print("FRECUENCIAS DE MAYOR A MENOR")
	ak.KanjiFrecuenciasMayorMenor() #Frecuencias de kanjis de mayor a menor
	print("---------------------------------------")
	print("---------------------------------------")
	print("NÚMERO DE PALABRAS POR KANJI DE MAYOR A MENOR")
	ak.WordsForKanji()# Palabras por kanji
	print("---------------------------------------")
	print("---------------------------------------")
	print("LAS DIEZ PALABRAS CON MAYOR FRECUENCIA POR KANJI")
	ak.frecuenciasPalabrasByKanji(True)# Frecuencias de palabras mayor frecuencia
	print("---------------------------------------")
	print("---------------------------------------")
	print("LAS DIEZ PALABRAS CON MENOR FRECUENCIA POR KANJI")
	ak.frecuenciasPalabrasByKanji(False)# Frecuencias de palabras menor frecuencia
	print("---------------------------------------")
	print("---------------------------------------")
	print("LAS PALABRAS CON MAYOR FRECUENCIA")
	ak.frecuenciasPalabrasN5(True)# Frecuencias de palabras N5 mayor frecuencia




#!/usr/bin/env python
# Stegapy
# Copyright 2013 J.A. Nache
# See LICENSE for details.

#python-PIL
import Image, sys, os

class UnestegFile:
	
	def __init__(self, pathOrigImage, pathDestFile):

		self.pathOrigImage = pathOrigImage
		self.pathDestFile = pathDestFile

		self.file = open(self.pathDestFile, 'wb')
		self.imageObj = Image.open(self.pathOrigImage)
		self.imgPix = self.imageObj.load()


	def readImgInBit(self):
		for x in range(0, self.imageObj.size[0]):
			for y in range(0, self.imageObj.size[1]):
				RGB = self.imgPix[x,y]
				for color in RGB:
					# return only the last bit in
					# R, G and B
					yield bin(color)[-1:]

	def unHide(self):
		bitcount = 0
		bytecount = 0
		byte = str()
		size = str()
		maxeof = 4294967295 # The largest file size in bytes we can hide
		bytes = self.readImgInBit()

		print("\nUnhidding file, wait...\n")
		for bit in bytes:

			byte += bit
			bitcount = bitcount + 1

			# We have a byte, so lets go
			# to work with they.
			if bitcount == 8:
				# count the number of bytes
				# to know when start an when stop
				bytecount = bytecount + 1

				# If we have four bytes,
				# we have the size of hiden
				# file. The next 'size' bytes
				# allow our file
				size +=byte
				if bytecount == 4:
					print('-> Size of hidden file: '+
							str(int( size ,2))+' bytes')
					print('\tAn extra 4 bytes (32bits) at header are skipped')
					print('\tThese extra 4 bytes are used to save the original file size')
					print('\tso its not part of file.')
					maxeof = int(size ,2)+4 #extra 4 bytes used for size at head

				# The first four bytes are used
				# for indicate the size of 
				# hidden file. We write only from
				# 5 to maxeof
				if bytecount > 4:
					self.file.write( chr( int( byte ,2)) )

				# reset the byte content
				# and the bit count
				byte = str()
				bitcount = 0

				# if the bytes writes are equal to
				# max of bytes hided, stop writing
				if bytecount == maxeof:
					break
		print ('\nDone')
		print ('==================================')
		print (str(bytecount - 4)+' bytes writed on file '+self.pathDestFile)


	def closeFile(self):
		self.file.close()


class EstegFile:

	def __init__(self, pathOrigFile, pathOrigImage, pathDestImage):

		self.pathOrigFile = pathOrigFile
		self.pathOrigImage = pathOrigImage
		self.pathDestImage = pathDestImage

		# The Source image
		self.imageObj = Image.open(self.pathOrigImage)
		self.imgPix = self.imageObj.load()

		# The Source file to hide
		self.file = open(self.pathOrigFile, 'rb')

		# The destination file with file hided
		# self.imageObj.size[0] -> Orig X size
		# self.imageObj.size[1] -> Orig Y size
		self.imageObjNew = Image.new("RGB", self.imageObj.size, "white")
		self.imgPixNew = self.imageObjNew.load()

	def saveDest(self):
		self.imageObjNew.save(self.pathDestImage,"PNG")

	def readFileInBit(self):
		# Reading file bit to bit using
		# yield instead return.
		# yield will return one bit
		# every time we call readFileInBit
		# function. The 32 first bits are
		# the representation of file size

		# first we send the file size
		fsize = os.fstat(self.file.fileno()).st_size
		for bit in bin(fsize)[2:].zfill(32):
			yield bit

		# now send the file bits
		while True:
			character = self.file.read(1)
			if not character:
				break
			else:
				byte = bin( ord( character ) )[2:].zfill(8)
				for bit in byte:
					yield bit


	def buildNew(self):
		# instancied inbytes for iterate
		inbytes = self.readFileInBit()
		bitscount = 0;
		
		print("\nHidding file, wait...")
		# Two 'for' are needed, one for run over
		# X and another to run over Y
		for x in range(0, self.imageObj.size[0]):
			for y in range(0, self.imageObj.size[1]):

				# Decompose pixel in R, G and B
				# every color chanel are represented
				# by one byte. We will use the LSB
				# (Least Significant Bit) to remplace
				# whith the bits values of our 'secret' file
				RGB = self.imgPix[x,y]	
				RGBnew = ()

				# Do this three times, one per
				# color channel. 
				for color in RGB:
					try:
						RGBnew = RGBnew + ( int( bin(color)[:-1]+inbytes.next() ,2), )
						bitscount = bitscount + 1
					# If we have this except, 
					# we are at the end of 'secret'
					# file, so copy the value of
					# channel intact.
					except StopIteration:
						RGBnew = RGBnew + (color, )

				# Save the value of new pixel
				self.imgPixNew[x,y] = RGBnew
			
		print ('\nDone')
		print ('==================================')
		print ('Orig File: '+self.pathOrigFile)
		print ('Hided with image: '+self.pathOrigImage)
		print ('Result File: '+self.pathDestImage)
		print ('==================================')
		print ('Hidded '+str(bitscount)+' bits | '
				+str(bitscount*0.125)+' bytes | '
				+str(bitscount*0.000122070312)+' kilobytes')
		print ('Extra 32 bits are used (represent the file size)')
				


def show_about():
	print('\n   Stegapy v0.1')
	print('   Copyright 2013 J.A. Nache under GPL v3\n')

def show_help():
	show_about()
	print ('\n   Usage')
	print ('   =========')
	print ('   Hide file:')
	print ('   '+sys.argv[0]+' h <File To Hide> <Source Image> <New Image File>')
	print ('\n   Unhide file:')
	print ('   '+sys.argv[0]+' u <Image with hidden data> <Dest File>\n')


try:
	if sys.argv[1] == 'h':
		show_about()
		sg = EstegFile(sys.argv[2], sys.argv[3], sys.argv[4])
		sg.buildNew()
		sg.saveDest()

	elif sys.argv[1] == 'u':
		show_about()
		sg = UnestegFile(sys.argv[2], sys.argv[3])
		sg.unHide()
		sg.closeFile()
	else:
		show_help()

except IndexError:
	show_help()

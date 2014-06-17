from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
import hashlib
import requests
import random
import json
# Constants
BACKEND_ADRESS = 'http://91.121.156.63/'
ADRESS_LENGTH = 34
PUPKEY_LENGTH = 130
SIGNATURE_LENGTH = 88
# Can handle a transaction containing all bitcoins. Can handle amounts as small a Satoshi. If the protocol changes to allow values of less than a satoshi, this constants would be changed.
BTC_MAX_DIGIT = 16
BTC_DECIMAL = 8

#Classes

class PubKey(models.Model):
	""" A user Public Key """
	value = models.CharField(max_length=PUPKEY_LENGTH,primary_key=True,help_text="Bitcoin public key")
	name  = models.CharField(max_length=30,help_text="A name defined by user to remember what is this public key for")
	comment = models.TextField(help_text="A note by the user")
	default = models.BooleanField(default=False,help_text="default key")
	user = models.ForeignKey('auth.User',help_text="The user who added this public key") # Link with the User of the auth package
	# TODO Add a address field in order to register the address associated to the public Key
	order = models.IntegerField(help_text="Reverse order to be displayed")
	active = models.BooleanField(default=True)
	
	class Meta:
		unique_together = (("user", "order")) # A user can't have multiple keys to be displayed on the same place
		
	def __unicode__(self): 
		if self.default:
			return "%s (default)" % (self.value,)
		else:
			return self.value
			
	def __init__(self, *args, **kwargs):
		super(PubKey, self).__init__(*args, **kwargs)
		if(not(self.order)):
			self.order=PubKey.objects.filter(user=self.user).count()+1 # Setting order
		if(not(self.default)):	
			if(PubKey.objects.all().filter(Q(user=self.user) & Q(default=True)).count()==0): # If this is the only key, put it default
				self.default=True
			
	def default_s(self):
		"Put this key as a default key. Modify the DB"
		PubKey.objects.filter(user=self.user).update(default=False)
		self.default=True
		self.save()
		

class PubKeyEscrow(models.Model):
	""" A public key linked with a private key that site admins can reconstitute offline """
	value = models.CharField(max_length=PUPKEY_LENGTH,primary_key=True,help_text="Bitcoin public key of the site")
	def __unicode__(self): 
		return self.value

TRANSACTION_STATUS = ( # The possible status of a transaction
	(1, 'Init'), # The transaction has just been initialised by the seller
	(2, 'Creation'), # The redeem script has just been created. This is after the seller gave its public key
	(3, 'Paid'), # The buyer sent the funds to the pay to script adress. Note that when a dispute appears, the transaction will be stucked on this status during the time of the dispute
	(4, 'Sent'), # The good have been sent. Or the service realised
	(5, 'Release'), # The funds have been released to some party. If no dispute is linked with this transaction, they are released to the vendor. Else see the dispute for more details. This status means that some party have the ability to move funds.
	(6, 'Cashout'), # The funds have been moved from the pay to hash adress.
)

class Transaction(models.Model):
	""" A transaction with where arbitration is possible """
	good = models.CharField(max_length=255,help_text="The name of the good or service bought")
	description = models.TextField(help_text="A detailed description of the good or service bought")
	price = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,help_text="The price in bitcoins of the good or service") 
	network_fee = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the network") 
	redeem_script = models.TextField(null=True,blank=True,help_text="The script to redem the content of the adress")
	adress = models.CharField(max_length=ADRESS_LENGTH,default='',blank=True,help_text="The pay to hash adress")
	escrow_fee_buyer = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the escrow by the buyer") 
	escrow_fee_seller = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the escrow by the seller") 
	datetime_init = models.DateTimeField(help_text="When the transaction was initialised by the seller")
	datetime_creation = models.DateTimeField(null=True,blank=True,help_text="When the script was created. When the buyer gives its public key")
	#Since the following operation can be managed without the need of the site, this fields can be kept NULL in some cases. Even after their transaction is finished
	datetime_paid = models.DateTimeField(null=True,blank=True,help_text="When the paiment was made")
	datetime_sent = models.DateTimeField(null=True,blank=True,help_text="When the good was sent")
	datetime_release = models.DateTimeField(null=True,blank=True,help_text="When the transaction was ready to be redeemed")
	datetime_cashout = models.DateTimeField(null=True,blank=True,help_text="When the bitcoins are transfered from the adress")
	seller_key = models.ForeignKey('PubKey',related_name='transaction_seller_key',help_text="The seller public key") # Never modify this two fields
	seller_id = models.ForeignKey('auth.User', related_name='transaction_seller', help_text="The seller id") # Never modify this field or set without a method
	buyer_key = models.ForeignKey('PubKey',related_name='transaction_buyer_key',null=True,blank=True,help_text="The buyer public key")
	buyer_id = models.ForeignKey('auth.User', related_name='transaction_buyer', blank=True, null=True, help_text="The buyer id") # To be deleted (remplaced by a method)
	escrow = models.OneToOneField('PubKeyEscrow',null=True,blank=True,help_text="The public key controlled linked with private key controlled by administrators")
	token = models.CharField(max_length=255,help_text="The token to use in url to send by email",unique=True)
	status = models.PositiveSmallIntegerField(choices=TRANSACTION_STATUS,default=1,help_text="The status of the transaction")
	canceled = models.BooleanField(default=False,help_text="True if the transaction canceled. Don't delete them to cancel them")
	signature_seller = models.CharField(max_length=88,default='',blank=True,help_text="Seller signature")
	signature_buyer = models.CharField(max_length=88,default='',blank=True,help_text="Buyer signature")
	signature_escrow = models.CharField(max_length=88,default='',blank=True,help_text="Escrow signature")
	
	def is_cancellable(self):
		"True if we can cancel the transaction"
		return (self.status==1 and not(canceled))
	
	def cancel(self):
		"Cancel the transaction. Return True if it succeded."
		if(self.status==1):
			self.canceled=True
			return True
		else:
			return False

	def __init__(self, *args, **kwargs):
		"Transaction initialisation"
		super(Transaction, self).__init__(*args, **kwargs)
		if(not(self.datetime_init)):
			self.datetime_init=timezone.now()
		if(not(self.token)):
			self.token=hashlib.md5(str(self.seller_key)+str(timezone.now())).hexdigest()
		if(not(hasattr(self, 'seller_id'))):
			self.seller_id=self.seller_key.user
	
	def seller(self):
		"The seller"
		if (self.seller_key):
			return self.seller_key.user
		else :
			return None

	def get_status_name(self):
		""" Returns the name of the current status """
		if self.status == 1:
			return "Transaction initialized"
		elif self.status == 2:
			return "Transaction initialization finished"
		elif self.status == 3:
			return "Transaction paid"
		elif self.status == 4:
			return "Transaction finished"
		elif self.status == 5:
			return "Funds moved out of the p2sh address"

	def buyer(self):
		"The buyer"
		if (self.buyer_key):
			return self.seller_key.user
		else :
			return None
			
	def buyer_price(self):
		"The price to be paid by the buyer"
		return self.price+self.escrow_fee_buyer
		
	def seller_price(self):
		"The price to be paid to seller"
		return self.price - self.network_fee - self.escrow_fee_seller
		
	def creation(self,buyer_key,escrow_fee_buyer=0):
		"Creation of the adress"
		self.escrow=PubKeyEscrow.objects.all().filter(transaction=None)[0] # We take a non-used Escrow Public Key
		self.buyer_key=buyer_key
		self.buyer_id=self.buyer_key.user
		self.escrow_fee_buyer=escrow_fee_buyer
		self.datetime_creation=timezone.now()
		self.status=2
		keys=[self.buyer_key.value, self.seller_key.value, self.escrow.value]
		random.shuffle(keys)
		payload = {'pubkeys': keys, 'id': self.id}
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		response = requests.post(BACKEND_ADRESS+'address/', data=json.dumps(payload), headers=headers)
		if response.status_code != 200:
			print "Unable to reach backend"
			return False
		data = response.json()
		self.redeem_script = data['redeemScript']
		self.adress=data['adress']
		return True
		
	def payment(self,time_paid=timezone.now()):
		"The buyer has sent coins to the P2H adress"
		if(self.status==2):
			self.datetime_paid=time_paid
			self.status=3
			return True
		else:
			return False
	
	def send(self,time_send=timezone.now()):
		"The seller sent the item or provided the service"
		self.status=4
		# Send a mail to buyer
	
	def release(self,time_release=timezone.now()):
		"One party decided to release the funds to another"
		self.datetime_release=time_release
		self.status=5
		# Send a mail to seller
		
	def cashout(self,time_cashout=timezone.now()):
		"The BTC in the P2H adress have been moved"
		self.datetime_cashout=time_cashout
		self.status=6
		

	def get_dispute_status(self):
		""" Return the status of the dispute. Return None if there is no dispute. """
		try:
			s=DisputeStatusChange.objects.filter(transaction=self).latest()
		except DisputeStatusChange.DoesNotExist:
			return None
		else:
			return s.new_status.name
	
	def start_dispute(self):
		""" Start a dispute. Return False if a dispute is already started. """
		if(not(self.get_dispute_status())):
			s=DisputeStatus.objects.get(reach_modality=0)
			DisputeStatusChange.create(self,s).save()
			return True
		else:
			return False
	
	def get_role(self,key):
		""" Give the role in this transaction associated with the key. An admin is not escrow on his own transactions. """
		if(self.seller_key==key):
			return 'seller'
		elif(self.buyer_key==key):
			return 'buyer'
		elif(key.user.is_superuser):
			return 'escrow'
		else:
			return None
	
	def add_dispute_message(self,user_key,title,content,status=None,visible=True,signature='',attachment=None):
		""" Add a dispute message. Can change the transaction status. """
		d=DisputeMessage(user=user_key,title=title,content=content,visible=visible,attachment=attachment,status=status,signature=signature,transaction=self,datetime_event=timezone.now())
		d.save()
		if(status): # If there is a status change demand
			role=self.get_role(user_key)
			if(role=='escrow'): # Status changed by escrow
				DisputeStatusChange.create(self,status,user_key).save()
			elif(status.reach_modality==1): # Status that anyone can change
				DisputeStatusChange.create(self,status).save()
			elif(status.reach_modality==2): # We need both to change
				try:
					s=DisputeMessage.objects.filter(transaction=self).exclude(user=user_key).exclude(status=None).latest() # Last message with status not written by the user
				except DisputeMessage.DoesNotExist:
					pass
				else:
					if(s.status==status): # Both asked to change to the same status
						DisputeStatusChange.create(self,status).save() 
			
		
		
		
REACH_MODALITY = (
	(0, 'Default'), # This is the status at the start of the dispute
	(1, 'Anyone'), # Any user can reach this status
	(2, 'Both'), # Both users should agree to reach this status
	(3, 'Escrow'), # Only the escrow can reach this status
)

class DisputeStatus(models.Model):
	""" A possible status in a dispute """
	name = models.CharField(max_length=30,help_text="The name of this status")
	description = models.TextField(help_text="The discription of the status")
	previous_status = models.ManyToManyField('self',null=True,blank=True,symmetrical=False,help_text="The status that can reach this one")
	reach_modality = models.PositiveSmallIntegerField(choices=REACH_MODALITY,help_text="How we can reach this status")
	day_to_reach = models.PositiveSmallIntegerField(default=0,help_text="Number of days to wait in the previous status to reach this one") # Does not apply to admins
	action_name = models.CharField(max_length=100,blank=True,help_text="The name of the action to go to this status")
	buyer_instruction = models.TextField(default="",blank=True,help_text="Instruction for the buyer")
	seller_instruction = models.TextField(default="",blank=True,help_text="Instruction for the seller")
	def __unicode__(self): 
		return self.name

class DisputeEvent(models.Model):
	""" An displayable event in a dispute """
	transaction = models.ForeignKey('Transaction',help_text="The transaction where the dispute event occures")
	datetime_event = models.DateTimeField(help_text="The date of the event")
	class Meta:
		abstract = True

class DisputeStatusChange(DisputeEvent):
	""" A status change. Can occure when buyer and seller agree to change the status. Or by an admin """
	new_status = models.ForeignKey('DisputeStatus',help_text="The new status")
	admin = models.ForeignKey('Pubkey',null=True,blank=True,help_text="The public key of the user initiating the change") # The admin Pubkey if the change is made by the admin. Null if the change is made by both parties	
	class Meta:
		unique_together = (("transaction", "datetime_event")) # The status can't change twice at the same time
		get_latest_by = 'datetime_event'

	@staticmethod
	def create(transaction, status, admin=None,datetime_event=timezone.now()):
		d=DisputeStatusChange(new_status=status,admin=admin,transaction=transaction,datetime_event=datetime_event)
		return d

	
class DisputeMessage(DisputeEvent):
	""" A dispute message. Can ask to change the status. """
	user = models.ForeignKey('Pubkey',help_text="The poster") 
	title = models.CharField(max_length=40,help_text="The title of the message")
	content = models.TextField(help_text="The content of the message")
	visible = models.BooleanField(help_text="Is this message visible by the other party? If False, only visible by the escrow")
	attachment = models.FileField(upload_to="attachment")
	status = models.ForeignKey('DisputeStatus',null=True,blank=True,help_text="An optional vote to go to a new status") # If the last messages of both parties ask for a new status, we move to this status
	signature = models.CharField(max_length=SIGNATURE_LENGTH,help_text="The signature of title, content and transaction id")
	
	class Meta:
		unique_together = (("datetime_event", "user")) # Only one post per user at the same time
		get_latest_by = 'datetime_event'
	def __unicode__(self): 
		return self.title

# Still in modification
# To change to a class
DISPUTE_STATUS = (
	(1, 'Amicable'), # The dispute has been initialised by one party. The parties are asked to try to find an amicable agreement.
	(2, 'Dispute Completion'), # The parties had not managed to agree. They have to gather evidences to support their case.
	(3, 'Additional Evidence'), # The parties are asked additional evidence by the escrow.
	(4, 'Escrow Verdict'), # The Escrow has given its verdict. Parties have the possibility to appeal to justice.
	(5, 'Escrow Verdict Accepted'), # The verdict of the escrow has been accepted.
	
	(10, 'Appeal'), # One party does not agree with the escrow decision. The case has to be brought to justice.
	(11, 'Justice'), # Some proof have been given that an action in justice have been engaged.
	(12, 'Justice Verdict'), # The verdict has been given by a justice court. We need to confirm the verdict authenticity.
	(13, 'Justice Appeal'), # One party has appealed the verdict in justice to an higher court. We keep this status as long there is other possible appeals
	(14, 'Justice Final Verdict'), # The appeal is final. There is no other possibilities of appeal
	
	(20, 'Validity of verdict documents contestation'), # The verdict documents provided are contested by a party
	(21, 'Validity of verdict documents accepted'), # Both parties have accepted the justice verdict
	
	(30, 'Escrow Signature'), # The escrow has signed a transaction
	(31, 'Amicable End'), # The two users agredded on the outcome
)



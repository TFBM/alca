from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Constants

#Instruction pour le shell
""" 
from transactions.models import PubKey
from django.contrib.auth.models import User
"""
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
		self.order=PubKey.objects.filter(user=self.user).count()+1
		
			
	def default_s(self):
		"Put this key as a default key. Modify the DB"
		PubKey.objects.filter(user=self.user).update(default=False)
		self.default=True
		self.save()
		

class PubkeyEscrow(models.Model):
	""" A public key linked with a private key that site admins can reconstitute offline """
	value = models.CharField(max_length=PUPKEY_LENGTH,primary_key=True,help_text="Bitcoin public key of the site")
	def __unicode__(self): 
		return self.value

TRANSACTION_STATUS = ( # The possible status of a transaction
	(1, 'Init'), # The transaction has just been initialised by the seller
	(2, 'Creation'), # The redeem script has just been created. This is after the seller gave its public key
	(3, 'Paid'), # The buyer sent the funds to the pay to script adress. Note that when a dispute appears, the transaction will be stucked on this status during the time of the dispute
	(4, 'Release'), # The funds have been released to some party. If no dispute is linked with this transaction, they are released to the vendor. Else see the dispute for more details
	(5, 'Cashout'), # The funds have been moved from the pay to hash adress
)

class Transaction(models.Model):
	""" A transaction with where arbitration is possible """
	good = models.CharField(max_length=255,help_text="The name of the good or service bought")
	description = models.TextField(help_text="A detailed description of the good or service bought")
	price = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,help_text="The price in bitcoins of the good or service") 
	network_fee = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the network") 
	redeem_script = models.TextField(null=True,blank=True,help_text="The script to redem the content of the adress")
	escrow_fee_buyer = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the escrow by the buyer") 
	escrow_fee_seller = models.DecimalField(max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL,null=True,blank=True,help_text="The fee given to the escrow by the seller") 
	datetime_init = models.DateTimeField(help_text="When the transaction was initialised by the seller")
	datetime_creation = models.DateTimeField(null=True,blank=True,help_text="When the script was created. When the buyer gives its public key")
	#Since the following operation can be managed without the need of the site, this fields can be kept NULL in some cases. Even after their transaction is finished
	datetime_paid = models.DateTimeField(null=True,blank=True,help_text="When the paiment was made")
	datetime_release = models.DateTimeField(null=True,blank=True,help_text="When the transaction was ready to be redeemed")
	datetime_cashout = models.DateTimeField(null=True,blank=True,help_text="When the bitcoins are transfered from the adress")
	seller_key = models.ForeignKey('PubKey',related_name='transaction_seller_key',help_text="The seller public key")
	seller_id = models.ForeignKey('auth.User', related_name='transaction_seller', help_text="The seller id") # To be deleted (replaced by a method)
	buyer_key = models.ForeignKey('PubKey',related_name='transaction_buyer_key',null=True,blank=True,help_text="The buyer public key")
	buyer_id = models.ForeignKey('auth.User', related_name='transaction_buyer', blank=True, null=True, help_text="The buyer id") # To be deleted (remplaced by a method)
	escrow = models.ForeignKey('PubKeyEscrow',help_text="The public key controlled linked with private key controlled by administrators")
	token = models.CharField(max_length=255,help_text="The token to use in url to send by email")
	status = models.PositiveSmallIntegerField(choices=TRANSACTION_STATUS,help_text="The status of the transaction")
	canceled = models.BooleanField(default=False,help_text="True if the transaction canceled. Don't delete them to cancel them")

#	def __init__(self,good,description,price,seller_id,seller_key,escrow,token,escrow_fee_seller=0):
#		"Transaction initialisation"
#		super(Transaction, self).__init__()
#		self.good=good
#		self.description=description
#		self.price=price
#		self.seller_id=seller_id
#		self.seller_key=seller_key
#		self.escrow_fee_seller=escrow_fee_seller
#		self.escrow = escrow
#		self.token = token
#		self.datetime_init=timezone.now()
#		self.status=1
	
	def seller(self):
		"The seller"
		if (self.seller_key):
			return self.seller_key.user
		else :
			return None

	def buyer(self):
		"The buyer"
		if (self.buyer_key):
			return self.seller_key.user
		else :
			return None

	def adress(self):
		"The pay to hash adress"
		if (self.redeem_script):
			raise NotImplementedError # Call the API to determine the adress
		else :
			return None
			
	def buyer_price(self):
		"The price to be paid by the buyer"
		return self.price+self.escrow_fee_buyer
		
	def seller_price(self):
		"The price to be paid to seller"
		return self.price - self.network_fee - self.escrow_fee_seller
		
	def creation(self,buyer,escrow_fee_buyer=0):
		"Creation of the adress"
		self.buyer=buyer
		self.escrow_fee_buyer=escrow_fee_buyer
		self.datetime_creation=timezone.now()
		self.status=2
		self.redeem_script='' #Not implemented yet. Call the API to create the script
		
	def payment(self,time_paid=timezone.now()):
		"The buyer has sent coins to the P2H adress"
		self.datetime_paid=time_paid
		self.status=3
	
	def release(self,time_release=timezone.now()):
		"One party decided to release the funds to another"
		self.datetime_release=time_release
		self.status=4
		
	def cashout(self,time_cashout=timezone.now()):
		"The BTC in the P2H adress have been moved"
		self.datetime_cashout=time_cashout
		self.status=5



REACH_MODALITY = (
	(0, 'Impossible'),
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
		unique_together = (("transaction", "datetime_event")) # The status can't change twice in the same time
	def __unicode__(self): 
		return self.new_status
	
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



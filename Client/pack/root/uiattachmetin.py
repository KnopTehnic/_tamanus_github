import dbg
import player
import item
import net
import snd
import ui
import uiToolTip
import localeInfo
import app
import mouseModule
import constInfo

class AttachMetinDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadScript()
		if app.ENABLE_ADDITIONAL_INVENTORY:
			self.baseinv = 0
			self.stoneinv = 0
		self.metinItemPos = 0
		self.targetItemPos = 0
		self.interface = None

	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/attachstonedialog.py")

		except:
			import exception
			exception.Abort("AttachStoneDialog.__LoadScript.LoadObject")

		try:
			self.board = self.GetChild("Board")
			self.titleBar = self.GetChild("TitleBar")
			self.metinImage = self.GetChild("MetinImage")
			self.GetChild("AcceptButton").SetEvent(ui.__mem_func__(self.Accept))
			self.GetChild("CancelButton").SetEvent(ui.__mem_func__(self.Close))
		except:
			import exception
			exception.Abort("AttachStoneDialog.__LoadScript.BindObject")

		oldToolTip = uiToolTip.ItemToolTip()
		oldToolTip.SetParent(self)
		oldToolTip.SetPosition(15, 38)
		oldToolTip.SetFollow(False)
		oldToolTip.Show()
		self.oldToolTip = oldToolTip

		newToolTip = uiToolTip.ItemToolTip()
		newToolTip.SetParent(self)
		newToolTip.SetPosition(230 + 20, 38)
		newToolTip.SetFollow(False)
		newToolTip.Show()
		self.newToolTip = newToolTip

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.board = 0
		self.titleBar = 0
		self.metinImage = 0
		self.toolTip = 0
		if app.ENABLE_ADDITIONAL_INVENTORY:
			self.baseinv = 0
			self.stoneinv = 0

	def BindInterfaceClass(self, interface):
		self.interface = interface

	def CanAttachMetin(self, slot, metin):
		if item.METIN_NORMAL == metin:
			if player.METIN_SOCKET_TYPE_SILVER == slot or player.METIN_SOCKET_TYPE_GOLD == slot:
				return True

		elif item.METIN_GOLD == metin:
			if player.METIN_SOCKET_TYPE_GOLD == slot:
				return True

	def Open(self, metinItemPos, targetItemPos):
		self.metinItemPos = metinItemPos
		self.targetItemPos = targetItemPos

		if app.ENABLE_ADDITIONAL_INVENTORY:
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
			if player.INVENTORY == attachedInvenType:
				metinIndex = player.GetItemIndex(metinItemPos)
				self.baseinv = 1
			else:
				metinIndex = player.GetItemIndex(player.STONE_INVENTORY, metinItemPos)
				self.stoneinv = 1
		else:
			metinIndex = player.GetItemIndex(metinItemPos)
		itemIndex = player.GetItemIndex(targetItemPos)
		self.oldToolTip.ClearToolTip()
		self.newToolTip.ClearToolTip()

		item.SelectItem(metinIndex)

		if app.ENABLE_SLOT_MARKING_SYSTEM:
			constInfo.ATTACH_METIN_ITEMS[0] = (attachedInvenType, metinItemPos)
			constInfo.ATTACH_METIN_ITEMS[1] = (player.INVENTORY, targetItemPos)

		## Metin Image
		try:
			self.metinImage.LoadImage(item.GetIconImageFileName())
		except:
			dbg.TraceError("AttachMetinDialog.Open.LoadImage - Failed to find item data")

		## Old Item ToolTip
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
		if app.ENABLE_ITEM_EVOLUTION_SYSTEM:
			self.oldToolTip.AddItemData(itemIndex, metinSlot, 0, player.GetItemEvolution(targetItemPos), 0, 0, 0, 0, 0)
		else:
			self.oldToolTip.AddItemData(itemIndex, metinSlot)

		## New Item ToolTip
		item.SelectItem(metinIndex)
		metinSubType = item.GetItemSubType()

		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			slotData = metinSlot[i]
			if self.CanAttachMetin(slotData, metinSubType):
				metinSlot[i] = metinIndex
				break
		if app.ENABLE_ITEM_EVOLUTION_SYSTEM:
			self.newToolTip.AddItemData(itemIndex, metinSlot, 0, player.GetItemEvolution(targetItemPos), 0, 0, 0, 0, 0)
		else:
			self.newToolTip.AddItemData(itemIndex, metinSlot)

		self.UpdateDialog()
		self.SetTop()
		self.Show()
		self.Refresh()

	def Refresh(self):
		if self.interface and app.ENABLE_SLOT_MARKING_SYSTEM:
			if self.interface.GetInventoryPtr():
				self.interface.GetInventoryPtr().RefreshBagSlotWindow()
			if self.interface.GetDragonSoulInventoryPtr():
				self.interface.GetDragonSoulInventoryPtr().RefreshBagSlotWindow()
			if app.ENABLE_ADDITIONAL_INVENTORY:
				if self.interface.GetSpecialStoragePtr():
					self.interface.GetSpecialStoragePtr().RefreshBagSlotWindow()

	def UpdateDialog(self):
		newWidth = self.newToolTip.GetWidth() + 230 + 15 + 20
		newHeight = self.newToolTip.GetHeight() + 98

		self.board.SetSize(newWidth, newHeight)
		self.titleBar.SetWidth(newWidth-15)
		self.SetSize(newWidth, newHeight)

		(x, y) = self.GetLocalPosition()
		self.SetPosition(x, y)

	def Accept(self):
		if app.ENABLE_ADDITIONAL_INVENTORY:
			if self.stoneinv == 1:
				net.SendItemUseToItemPacket(player.STONE_INVENTORY, self.metinItemPos, player.INVENTORY, self.targetItemPos)
			elif self.baseinv == 1:
				net.SendItemUseToItemPacket(self.metinItemPos, self.targetItemPos)
		else:
			net.SendItemUseToItemPacket(self.metinItemPos, self.targetItemPos)
		snd.PlaySound("sound/ui/metinstone_insert.wav")
		self.Close()

	def Close(self):
		self.Hide()
		constInfo.ATTACH_METIN_ITEMS = {}
		self.Refresh()
		if app.ENABLE_ADDITIONAL_INVENTORY:
			self.stoneinv = 0
			self.baseinv = 0

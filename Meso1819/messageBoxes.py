from PySide.QtGui import QMessageBox;

class baseMessage( QMessageBox ):
  def __init__(self, text, **kwargs):
    QMessageBox.__init__(self, **kwargs);
    self.setText( text );
  def check(self):
    return self.clickedButton() == self.accept;
    
class criticalMessage( baseMessage ):
  def __init__(self, text, **kwargs):
    baseMessage.__init__(self, text, **kwargs);
    self.setIcon( QMessageBox.Critical );
    self.accept = self.addButton( 'Okay', QMessageBox.YesRole );

class confirmMessage( baseMessage ):
  def __init__(self, text, **kwargs):
    baseMessage.__init__(self, text, **kwargs);
    self.setIcon( QMessageBox.Question );
    self.accept = self.addButton( 'Yes', QMessageBox.YesRole );
    self.reject = self.addButton( 'No',  QMessageBox.RejectRole );

class saveMessage( baseMessage ):
  def __init__(self, text, **kwargs):
    baseMessage.__init__(self, text, **kwargs);
    self.setIcon( QMessageBox.Critical );
    self.accept = self.addButton( 'Save',   QMessageBox.YesRole );
    self.reject = self.addButton( 'Cancel', QMessageBox.RejectRole );

import dropbox
from dropbox.files import WriteMode
from keys import ACCESS_TOKEN

dbx = dropbox.Dropbox(ACCESS_TOKEN)
print(dbx.users_get_current_account())

with open("Orrell Park Vet Schedule.pdf", "rb") as f:
    dbx.files_upload(f.read(), '/WHV Rotas/Orrell Park Vet Schedule.pdf', mode=WriteMode('overwrite'))

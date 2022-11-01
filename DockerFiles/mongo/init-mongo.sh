

##https://www.mongodb.com/docs/manual/reference/method/db.createUser/
##old method of create user doesnt work in Mongo6, also use mongosh for command line
#!/bin/bash
# https://stackoverflow.com/a/53522699
# https://stackoverflow.com/a/37811764
mongosh -- "$MONGO_INITDB_DATABASE" <<EOF
  var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
  var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
  var user = '$MONGO_INITDB_USERNAME';
  var passwd = '$MONGO_INITDB_PASSWORD';
  var userDB = '$MONGO_INITDB_DATABASE';
  
  var admin = db.getSiblingDB('admin');
  var varUserDB = db.getSiblingDB(userDB);

  admin.auth(rootUser, rootPassword);
  
  varUserDB.createUser({
    user: user,
    pwd: passwd,
    roles: [ "readWrite", "dbAdmin" ]
  });
EOF



# mongosh -- "$MONGO_INITDB_DATABASE" <<EOF
#   var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
#   var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
#   var user = '$MONGO_INITDB_USERNAME';
#   var passwd = '$MONGO_INITDB_PASSWORD';
  
#   var admin = db.getSiblingDB('admin');

#   admin.auth(rootUser, rootPassword);

#     use walletProfileDB;
#   db.createUser({
#     user: user,
#     pwd: passwd,
#     roles: [ "readWrite", "dbAdmin" ]
#   });
# EOF



# db.createUser({
#     user: "user",
#     pwd: "passwd",
#     roles: [ "readWrite", "dbAdmin" ]
#   });

# db.createUser({
#     user: "adminuser",
#     pwd: "venice556",
#     roles: [
#       {
#         role: "root",
#         db: "app_db"
#       }
#     ]
#   });
# db.createUser({
#     user: "b",
#     pwd: "b",
#     roles: [{role: "dbOwner", db: "randomDB"}]
#   });


# #   use products
# # db.createUser(
# #    {
# #      user: "user",
# #      pwd: passwordPrompt(),  // Or  "<cleartext password>"
# #      roles: [ "readWrite", "dbAdmin" ]
# #    }
# # )

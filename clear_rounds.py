import implementation
import json
import database
import os


db = database.Database("sqlite:///testing.db")
impl = implementation.Implementation(db.models, db.session)

impl.delete_all_rounds()


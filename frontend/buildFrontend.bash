echo deleting old dist
cd ../
cd backend
rm -r dist

echo making new dist
cd ../
cd frontend
npm run build


echo copying new dist to backend
cp -r dist ../backend/


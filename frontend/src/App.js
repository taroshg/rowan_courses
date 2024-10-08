import React, { useEffect, useState } from 'react';
import { FaCopy } from "react-icons/fa";
import './App.css';
import catalog from './catalog.json'
import professors_json from './profs.json'
import tally from './tally.json'


const courses = Object.keys(catalog).map(key => catalog[key]);
const professors = Object.keys(professors_json).map(key => professors_json[key]);
const tallyData = Object.keys(tally).map(key => tally[key]);

function CourseLoader() {

  let elements = []

  for (const course of courses) {
    let classes = tallyData.filter(cls => (cls.Subj === course.subj) && (cls.Crse === course.crse))
    elements.push(<Course course={course} classes={classes}/>)
  }

  return (
    <div>
      {elements}
    </div>
  );
}

function ClassItem(props) {
  const [copyText, setCopyText] = useState('Copy CRN');
  const handleCopy = () => {
    navigator.clipboard.writeText(props.classItem['CRN']);
    setCopyText('Copied!');
    setTimeout(() => setCopyText('Copy CRN'), 2000);
  };

  let times = props.classItem['schedule'].split('\n')

  // TODO: make it more robust
  let prof = professors.filter(prof => {
    return prof.tLname.toLowerCase() === props.classItem['Prof'].split(',')[0].toLowerCase();
  })[0];

  return (
    <li className='class-item' onClick={handleCopy}>
      <span className='copy-crn'>{copyText} <FaCopy /> </span>
      <p>Professor: {props.classItem['Prof']}
        <span className='class-item-prof-rating'>{prof && 'rating: (' + prof.overall_rating + ' / 5)'}</span>
      </p>
      <div className='class-item-times'>
        {times.map((time, idx) => (
          <p key={idx}>{time.trim()}</p>
        ))}
      </div>
      <div className='class-item-enrollment'>
      {props.classItem['Enr'] > 0 && (
        <div>
          <p>Enrollment: {props.classItem['Enr']} / {props.classItem['Max']}</p>
          <progress value={props.classItem['Enr']} max={props.classItem['Max']}></progress>
        </div>
      )}
      </div>
      <div className='class-item-footer-info'><p>CRN: {props.classItem['CRN']} Section: {props.classItem['Sect']}</p></div>
    </li>
  )
}

function Course(props) {
  const [showClasses, setShowClasses] = useState(false);

  const toggleClasses = () => {
    setShowClasses(!showClasses);
  };

  return (
    <div className='course-container'>
      <div className='course-title'>{props.course.title}</div>
      <div className='course-desc'>{props.course.desc}</div>
      <button className='show-classes-button' onClick={toggleClasses}>
        {showClasses ? 'Hide Classes' : 'Show Classes'}
      </button>
      {showClasses && (
        <ul className='classes-container'>
          {props.classes.map((classItem, index) => (
            <ClassItem key={index} classItem={classItem} />
          ))}
        </ul>
      )}
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <CourseLoader />
      </header>
    </div>
  );
}

export default App;
